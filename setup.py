from setuptools import setup, find_packages

setup(
    name="files-melty-ai",
    version="0.1",
    description="Meltano knowledge base files for AI use.",
    packages=find_packages(),
    # bundle/ is the single seed image: AGENTS.md + CLAUDE.md + the shared KB under
    # .claude/meltano_knowledge_base/ + the golden-path reference project under
    # reference/. Ship it wholesale (every file type, not just *.md) via MANIFEST.in +
    # include_package_data so the reference's .yml/.lock/.py/.sql/.env.example/.gitkeep
    # files are not silently dropped.
    include_package_data=True,
)
