class LatexSanitizer:
    @staticmethod
    def escape(text: str) -> str:
        """
        Escapes reserved LaTeX characters in a string.
        """
        if not isinstance(text, str):
            return text

        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}'
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text

    @staticmethod
    def sanitize_payload(data):
        """
        Recursively traverses the JSON data and escapes all string values.
        """
        if isinstance(data, dict):
            return {k: LatexSanitizer.sanitize_payload(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [LatexSanitizer.sanitize_payload(item) for item in data]
        elif isinstance(data, str):
            return LatexSanitizer.escape(data)
        else:
            return data
