class LatexSanitizer:
    @staticmethod
    def escape(text: str) -> str:
        """
        Escapes reserved LaTeX characters in a string.
        Handles:
        1. Markdown links: [text](url) -> \href{url}{text}
        2. Markdown bold: **text** -> \textbf{text}
        """
        if not isinstance(text, str):
            return text

        import re

        # Regex patterns
        LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        BOLD_PATTERN = re.compile(r'\*\*([^*]+)\*\*')

        def escape_chars(s):
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
                s = s.replace(char, replacement)
            return s

        def process_bold(text_segment):
            """
            Parses **bold** inside a text segment (that is NOT a link).
            """
            parts = []
            last_idx = 0
            for match in BOLD_PATTERN.finditer(text_segment):
                # Text before bold
                pre_text = text_segment[last_idx:match.start()]
                parts.append(escape_chars(pre_text))
                
                # Bold content
                bold_content = match.group(1)
                safe_bold = escape_chars(bold_content)
                parts.append(f"\\textbf{{{safe_bold}}}")
                
                last_idx = match.end()
            
            # Text after last bold
            parts.append(escape_chars(text_segment[last_idx:]))
            return "".join(parts)

        # Main logic: Split by Links first
        last_idx = 0
        parts = []
        
        for match in LINK_PATTERN.finditer(text):
            # 1. Process text BEFORE the link (Check for bold here)
            pre_text = text[last_idx:match.start()]
            parts.append(process_bold(pre_text))
            
            # 2. Process the LINK itself
            label = match.group(1)
            url = match.group(2)
            
            # For the Label: It might contain bold text! (e.g. [**Click** me](url))
            # But usually links are simple. Let's assume label is simple text for now to avoid recursion hell, 
            # or just run process_bold on it if we want to be fancy. Let's stick to simple escaping for link labels for safety.
            safe_label = escape_chars(label) 
            safe_url = escape_chars(url)
            
            parts.append(f"\\href{{{safe_url}}}{{{safe_label}}}")
            
            last_idx = match.end()
        
        # 3. Process text AFTER the last link (Check for bold here)
        parts.append(process_bold(text[last_idx:]))
        
        return "".join(parts)

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
