import os
import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from dotenv import load_dotenv
import google.generativeai as genai


class GeminiGeneratorService:
    """
    Gemini Generator Service - Generates AI-powered feedback using Google's Gemini API.
    Implements rate limiting and retry logic.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Gemini Generator Service."""
        self.config = self._load_config(config_path)
        self._setup_logging()
        self._setup_gemini_api()
        self.last_request_time = 0

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        else:
            config_path = Path(config_path)

        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config['logging']['level'])
        log_file = Path(self.config['logging']['file'])

        # Create logs directory if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.config['service']['name'])
        self.logger.info(f"Initialized {self.config['service']['name']} v{self.config['service']['version']}")

    def _setup_gemini_api(self):
        """Setup Gemini API with credentials."""
        # Load environment variables
        load_dotenv()

        # Get API key from environment
        api_key_env = self.config['gemini']['api_key_env']
        api_key = os.getenv(api_key_env)

        if not api_key:
            self.logger.error(f"API key not found in environment variable: {api_key_env}")
            raise ValueError(f"Missing environment variable: {api_key_env}")

        # Configure Gemini API
        genai.configure(api_key=api_key)

        # Initialize the model
        self.model = genai.GenerativeModel(self.config['gemini']['model'])
        self.logger.info(f"Gemini API configured with model: {self.config['gemini']['model']}")

    def _apply_rate_limiting(self):
        """Apply rate limiting between requests."""
        delay = self.config['rate_limiting']['request_delay_seconds']
        elapsed = time.time() - self.last_request_time

        if elapsed < delay:
            wait_time = delay - elapsed
            self.logger.info(f"Rate limiting: waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)

        self.last_request_time = time.time()

    def _generate_feedback_with_retry(self, prompt: str, style: str) -> Dict[str, Any]:
        """
        Generate feedback with retry logic.

        Returns:
            Dict with feedback, status, error, and tokens_used
        """
        max_retries = self.config['rate_limiting']['max_retries']
        retry_delay = self.config['rate_limiting']['retry_delay_seconds']

        for attempt in range(max_retries):
            try:
                # Apply rate limiting
                self._apply_rate_limiting()

                # Prepare the full prompt with style
                full_prompt = f"Style: {style}\n\n{prompt}"

                # Generate content
                self.logger.info(f"Generating feedback (attempt {attempt + 1}/{max_retries})")

                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=self.config['generation']['max_tokens'],
                        temperature=self.config['generation']['temperature']
                    )
                )

                # Extract feedback text
                feedback_text = response.text

                # Calculate tokens used (approximation)
                tokens_used = len(full_prompt.split()) + len(feedback_text.split())

                self.logger.info(f"Successfully generated feedback ({tokens_used} tokens)")

                return {
                    "feedback": feedback_text,
                    "status": "Success",
                    "error": None,
                    "tokens_used": tokens_used
                }

            except Exception as e:
                error_msg = str(e)
                self.logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")

                # Check for specific error types
                if "API_KEY" in error_msg.upper() or "INVALID" in error_msg.upper():
                    self.logger.error("Invalid API key detected")
                    return {
                        "feedback": None,
                        "status": "Failed",
                        "error": "Invalid API key",
                        "tokens_used": 0
                    }

                # If not the last attempt, wait before retrying
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    # Last attempt failed
                    self.logger.error(f"All retry attempts failed: {error_msg}")
                    return {
                        "feedback": None,
                        "status": "Failed",
                        "error": error_msg,
                        "tokens_used": 0
                    }

        # Should never reach here, but just in case
        return {
            "feedback": None,
            "status": "Failed",
            "error": "Max retries exceeded",
            "tokens_used": 0
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and generate feedback.

        Input format:
        {
            "prompt": str,
            "style": str,
            "context": {
                "grade": float,
                "email_id": str
            }
        }

        Output format:
        {
            "feedback": str | None,
            "status": str,
            "error": str | None,
            "tokens_used": int
        }
        """
        try:
            # Validate input
            if "prompt" not in input_data or "style" not in input_data:
                self.logger.error("Missing required fields in input")
                return {
                    "feedback": None,
                    "status": "Failed",
                    "error": "Missing required fields: prompt and/or style",
                    "tokens_used": 0
                }

            prompt = input_data["prompt"]
            style = input_data["style"]
            context = input_data.get("context", {})

            self.logger.info(f"Processing request for email_id: {context.get('email_id', 'N/A')}")

            # Generate feedback with retry logic
            result = self._generate_feedback_with_retry(prompt, style)

            return result

        except Exception as e:
            self.logger.error(f"Unexpected error in process: {str(e)}")
            return {
                "feedback": None,
                "status": "Failed",
                "error": f"Unexpected error: {str(e)}",
                "tokens_used": 0
            }

    def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        try:
            # Simple health check - verify API key is configured
            api_key = os.getenv(self.config['gemini']['api_key_env'])
            api_configured = api_key is not None and len(api_key) > 0

            return {
                "service": self.config['service']['name'],
                "version": self.config['service']['version'],
                "status": "healthy" if api_configured else "unhealthy",
                "api_configured": api_configured
            }
        except Exception as e:
            return {
                "service": self.config['service']['name'],
                "version": self.config['service']['version'],
                "status": "unhealthy",
                "error": str(e)
            }
