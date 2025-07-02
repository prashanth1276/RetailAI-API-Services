"""import requests
import logging
from langchain.prompts import PromptTemplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DescriptionGenerator:
    def __init__(self, model="llama3"):
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.prompt_template = PromptTemplate(
            input_variables=["name", "category", "material"],
            template="Generate a 3-sentence, SEO-friendly product description for a {category} product named '{name}' made of {material}. "
                     "Include keywords like '{category} {name}', 'best {category}', and 'high-quality {material}' to boost searchability. "
                     "Highlight key features, appeal to the target audience, and include a call to action."
        )

    def generate_description(self, name: str, category: str, material: str):
        prompt = self.prompt_template.format(name=name, category=category, material=material)
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            result = response.json().get("response", "").strip()
            return result.split("<|end_header_id>")[-1].strip() if "<|end_header_id>" in result else result
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            return f"Error generating description: {e}"

description_generator = DescriptionGenerator()
"""



import requests
import logging
from langchain.prompts import PromptTemplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DescriptionGenerator:
    def __init__(self, model="llama3"):
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.prompt_template = PromptTemplate(
            input_variables=["name", "category", "material"],
            template="Generate a 3-sentence, SEO-friendly product description (max 100 tokens) for a {category} product named '{name}' made of {material}. "
                     "Include keywords like '{category} {name}', 'best {category}', and 'high-quality {material}' to boost searchability. "
                     "Highlight key features and a call to action."
        )

    def generate_description(self, name: str, category: str, material: str):
        prompt = self.prompt_template.format(name=name, category=category, material=material)
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            result = response.json().get("response", "").strip()
            return result.split("<|end_header_id>")[-1].strip() if "<|end_header_id>" in result else result
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            return f"Error generating description: {e}"

description_generator = DescriptionGenerator()