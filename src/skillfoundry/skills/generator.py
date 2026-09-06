"""
Skill generation from project analysis using LLMs.
"""
from __future__ import annotations

import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from skillfoundry.providers.base import ModelProvider, GenerateRequest
from skillfoundry.models.skill import GeneratedSkill, SkillMetadata, ReferenceFile, SkillClaim
from skillfoundry.models.analysis import ProjectAnalysis
from skillfoundry.config import Settings
from skillfoundry.skills.naming import generate_skill_name
from skillfoundry.analysis.context import select_context

logger = logging.getLogger(__name__)

class SkillGenerationOutput(BaseModel):
    """Structured output schema for skill generation."""
    description: str = Field(description="Description of what the skill does")
    skill_body: str = Field(description="Markdown content of SKILL.md body")
    references: list[dict] = Field(description="List of reference files (filename, content)")
    key_capabilities: list[str] = Field(description="Key capabilities of the skill")
    claims: list[dict] = Field(description="Claims with provenance (claim, source_file, confidence)")

class SkillGenerator:
    """Generates Agent Skills from project analysis."""
    
    def __init__(self, provider: ModelProvider, settings: Settings):
        self.provider = provider
        self.settings = settings
        
    def generate(self, analysis: ProjectAnalysis) -> GeneratedSkill:
        """
        Generate a complete skill from the provided project analysis.
        """
        # 1. Build context
        context = select_context(analysis, self.settings)
        
        # 2. Generate name
        skill_name = generate_skill_name(analysis)
        
        # 3. System prompt
        system_prompt = (
            "You are an expert AI agent skill generator. "
            "Generate SKILL.md content based on the provided project context. "
            "Describe specifically what the skill helps an agent DO and WHEN to use it. "
            "Be specific, avoid vague descriptions. "
            "Use progressive disclosure: keep the SKILL.md concise and put detailed topics in references. "
            "DO NOT hallucinate APIs or commands not found in the source. "
            "Include ONLY information supported by the analysis."
        )
        
        request = GenerateRequest(
            system_prompt=system_prompt,
            prompt=f"Generate skill for project named '{skill_name}'. Context:\\n{context}",
            response_model=SkillGenerationOutput
        )
        
        # Call provider
        response_data = self.provider.structured_generate(request)
        if not isinstance(response_data, SkillGenerationOutput):
            raise TypeError("Provider did not return a SkillGenerationOutput instance.")
            
        # 4. Parse and validate
        metadata = SkillMetadata(
            name=skill_name,
            description=response_data.description
        )
        
        # 5. Generate reference files
        reference_files = [
            ReferenceFile(
                filename=ref.get("filename", "ref.md"),
                content=ref.get("content", "")
            )
            for ref in response_data.references
        ]
        
        # 6. Track claims
        claims = [
            SkillClaim(
                claim=claim.get("claim", ""),
                source_file=claim.get("source_file", ""),
                confidence=claim.get("confidence", 0.0)
            )
            for claim in response_data.claims
        ]
        
        # 7. Return generated skill
        return GeneratedSkill(
            metadata=metadata,
            body=response_data.skill_body,
            references=reference_files,
            capabilities=response_data.key_capabilities,
            claims=claims
        )
