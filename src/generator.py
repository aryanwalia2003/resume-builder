import json
import os
from jinja2 import Environment, FileSystemLoader
from src.config import Config
from src.utils import LatexSanitizer

class ResumeGenerator:
    def __init__(self):
        self.config = Config.get_instance()
        self.env = Environment(
            loader=FileSystemLoader(str(self.config.TEMPLATE_DIR)),
            block_start_string=r'\BLOCK{',
            block_end_string=r'}',
            variable_start_string=r'\VAR{',
            variable_end_string=r'}',
            comment_start_string=r'\#{',
            comment_end_string=r'}',
            line_statement_prefix='%%',
            line_comment_prefix='%#',
            trim_blocks=True,
            autoescape=False,
        )

    def generate_tex(self, json_filename: str, template_name: str) -> str:
        # 1. Load JSON
        json_path = self.config.DATA_DIR / json_filename
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 2. Sanitize JSON
        sanitized_data = LatexSanitizer.sanitize_payload(data)

        # 3. Render Template
        template = self.env.get_template(template_name)
        return template.render(**sanitized_data)
