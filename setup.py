from setuptools import setup, find_packages

setup(
    name="files-melty-ai",
    version="0.1",
    description="Meltano knowledge base files for AI use.",
    packages=find_packages(),
    package_data={
        "bundle": [
            "CLAUDE.md",
            "AGENTS.md",
            ".claude/meltano_knowledge_base/meltano/*.md",
            ".claude/meltano_knowledge_base/meltano_cloud/*.md",
        ]
    },
)
