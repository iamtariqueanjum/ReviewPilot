import ast

from app.core.chunking.splitters.base_splitter import BaseSplitter


class PythonSplitter(BaseSplitter):

    def __init__(self):
        super().__init__()

    def split(self, payload):
        chunks = []
        try:
            lines = payload['file_content'].split("\n")
            tree = ast.parse(payload['file_content'])
            chunk_index = 1
            imports = self.extract_imports(tree)
            for node in ast.walk(tree):
                # def
                if isinstance(node, ast.FunctionDef):
                    start, end = node.lineno, node.end_lineno
                    chunk = "\n".join(lines[start:end])
                    chunk_id = f"chunk_{chunk_index}"
                    chunks.append({
                        "owner": payload['owner'],
                        "repo": payload['repo'],

                        "file_path": payload['file_path'],
                        "file_name": payload['file_name'],
                        "file_extension": payload['file_extension'],
                        "language": payload['language'],

                        "chunk_id": chunk_id,
                        "chunk_name": node.name,
                        "chunk_content": chunk, # TODO move to DB store from vector store
                        "chunk_index": chunk_index,
                        "chunk_start_line": start,
                        "chunk_end_line": end,

                        "imports": imports,
                        "commit_sha": payload['commit_sha']

                    })
                    chunk_index += 1
        except Exception as e:
            # TODO logger
            # TODO Fallback splitter
            raise e
        return chunks

    @staticmethod
    def extract_imports(tree):
        imports = []
        for node in ast.walk(tree):
            # import x, y
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            # from x import y
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    full_import = f"{module}.{alias.name}" if module else alias.name
                    imports.append(full_import)
        return imports