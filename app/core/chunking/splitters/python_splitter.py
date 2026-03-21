import ast

from app.core.chunking.splitters.base_splitter import BaseSplitter


class PythonSplitter(BaseSplitter):

    def __init__(self):
        super().__init__()

    def split(self, owner, repo, file_name, extension, language, file_content, file_path, commit_sha):
        chunks = []
        try:
            lines = file_content.split("\n")
            tree = ast.parse(file_content)
            chunk_index = 1
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
            for node in ast.walk(tree):
                # def
                if isinstance(node, ast.FunctionDef):
                    start, end = node.lineno, node.end_lineno
                    chunk = "\n".join(lines[start:end])
                    chunk_id = f"chunk_{chunk_index}"
                    chunks.append({
                        "id": f"{repo}:{file_path}:{chunk_id}",
                        "owner": owner,
                        "repo": repo,

                        "file_path": file_path,
                        "file_name": file_name,
                        "extension": extension,
                        "language": language,

                        "chunk_name": node.name,
                        "chunk_content": chunk,
                        "chunk_index": chunk_index,
                        "chunk_start_line": start,
                        "chunk_end_line": end,

                        "imports": imports,
                        "commit_sha": commit_sha

                    })
                    chunk_index += 1
        except Exception as e:
            # TODO logger
            # TODO Fallback splitter
            raise e
        return chunks