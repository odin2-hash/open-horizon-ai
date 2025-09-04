"""
Erasmus+ Knowledge Crawling Service

This module specializes the general crawling service for Erasmus+ programme documentation,
partner databases, and educational resources relevant to project planning and application writing.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .crawling_service import CrawlingService
from .helpers.site_config import SiteConfig


@dataclass
class ErasmusCrawlSource:
    """Configuration for Erasmus+ specific crawling sources."""
    url: str
    source_type: str  # 'programme_guide', 'partner_db', 'best_practices', 'calls'
    priority: int  # 1-10, higher = more important
    update_frequency_days: int
    description: str
    tags: List[str]


class ErasmusKnowledgeService(CrawlingService):
    """
    Specialized crawling service for Erasmus+ knowledge base.
    
    Focuses on crawling official programme documentation, partner databases,
    best practices, and relevant educational resources.
    """

    def __init__(self, crawler=None, supabase_client=None, progress_id=None):
        super().__init__(crawler, supabase_client, progress_id)
        
        # Erasmus+ specific crawl sources
        self.erasmus_sources = [
            ErasmusCrawlSource(
                url="https://erasmus-plus.ec.europa.eu/programme-guide",
                source_type="programme_guide",
                priority=10,
                update_frequency_days=30,
                description="Official Erasmus+ Programme Guide",
                tags=["official", "guide", "regulations"]
            ),
            ErasmusCrawlSource(
                url="https://erasmus-plus.ec.europa.eu/opportunities",
                source_type="calls",
                priority=9,
                update_frequency_days=7,
                description="Current funding opportunities and calls",
                tags=["funding", "calls", "deadlines"]
            ),
            ErasmusCrawlSource(
                url="https://erasmus-plus.ec.europa.eu/resources/best-practices",
                source_type="best_practices",
                priority=8,
                update_frequency_days=14,
                description="Best practices and successful projects",
                tags=["examples", "best-practices", "inspiration"]
            ),
            ErasmusCrawlSource(
                url="https://ec.europa.eu/programmes/erasmus-plus/projects/",
                source_type="project_database",
                priority=7,
                update_frequency_days=30,
                description="Database of funded projects",
                tags=["projects", "examples", "partners"]
            )
        ]

    async def crawl_erasmus_knowledge_base(self, focus_areas: List[str] = None) -> Dict[str, Any]:
        """
        Crawl Erasmus+ specific knowledge sources.
        
        Args:
            focus_areas: Optional list of focus areas to prioritize
                        (e.g., ['youth', 'digital', 'environment'])
        
        Returns:
            Dict containing crawl results and metadata
        """
        results = {
            "sources_crawled": 0,
            "documents_added": 0,
            "errors": [],
            "crawl_summary": {}
        }

        # Filter sources based on focus areas if provided
        sources_to_crawl = self._filter_sources_by_focus(focus_areas) if focus_areas else self.erasmus_sources
        
        # Sort by priority
        sources_to_crawl.sort(key=lambda x: x.priority, reverse=True)

        for source in sources_to_crawl:
            try:
                await self._crawl_erasmus_source(source, results)
            except Exception as e:
                results["errors"].append({
                    "source": source.url,
                    "error": str(e),
                    "type": source.source_type
                })

        return results

    async def _crawl_erasmus_source(self, source: ErasmusCrawlSource, results: Dict[str, Any]) -> None:
        """Crawl a specific Erasmus+ source."""
        print(f"📚 Crawling {source.description}: {source.url}")
        
        # Use appropriate crawling strategy based on source type
        if source.source_type == "programme_guide":
            crawl_result = await self._crawl_programme_guide(source)
        elif source.source_type == "partner_db":
            crawl_result = await self._crawl_partner_database(source)
        elif source.source_type == "best_practices":
            crawl_result = await self._crawl_best_practices(source)
        else:
            # Use general single page or recursive strategy
            crawl_result = await self.single_page_strategy.crawl_single_url(
                source.url,
                extract_markdown=True
            )

        if crawl_result and crawl_result.get("success"):
            # Store with Erasmus+ specific metadata
            await self._store_erasmus_document(source, crawl_result)
            results["sources_crawled"] += 1
            results["documents_added"] += len(crawl_result.get("documents", []))
            
            results["crawl_summary"][source.source_type] = {
                "url": source.url,
                "status": "success",
                "documents": len(crawl_result.get("documents", [])),
                "description": source.description
            }

    async def _crawl_programme_guide(self, source: ErasmusCrawlSource) -> Dict[str, Any]:
        """
        Specialized crawling for Erasmus+ Programme Guide.
        
        The programme guide is structured with multiple sections, so we use
        recursive crawling with specific depth and filtering.
        """
        return await self.recursive_strategy.crawl_recursive(
            source.url,
            max_depth=2,
            same_domain_only=True,
            extract_markdown=True,
            url_patterns=[
                r"/programme-guide/",
                r"/eligibility/",
                r"/budget/",
                r"/application/"
            ]
        )

    async def _crawl_partner_database(self, source: ErasmusCrawlSource) -> Dict[str, Any]:
        """
        Specialized crawling for partner databases.
        
        Partner databases often have search interfaces, so we need to handle
        dynamic content and pagination.
        """
        # This would integrate with partner search APIs or crawl search results
        return await self.batch_strategy.crawl_urls([source.url])

    async def _crawl_best_practices(self, source: ErasmusCrawlSource) -> Dict[str, Any]:
        """
        Specialized crawling for best practices and project examples.
        """
        return await self.recursive_strategy.crawl_recursive(
            source.url,
            max_depth=3,
            same_domain_only=True,
            extract_markdown=True,
            url_patterns=[
                r"/best-practices/",
                r"/success-stories/",
                r"/project-results/"
            ]
        )

    async def _store_erasmus_document(self, source: ErasmusCrawlSource, crawl_result: Dict[str, Any]) -> None:
        """
        Store crawled document with Erasmus+ specific metadata.
        """
        if not crawl_result.get("documents"):
            return

        for doc in crawl_result["documents"]:
            # Add Erasmus+ specific metadata
            doc["metadata"] = {
                **doc.get("metadata", {}),
                "source_type": source.source_type,
                "erasmus_priority": source.priority,
                "update_frequency": source.update_frequency_days,
                "erasmus_tags": source.tags,
                "programme": "Erasmus+",
                "relevant_for": self._determine_relevance(doc, source)
            }

            # Store using parent class storage operations
            await self.doc_storage_ops.store_document(doc)

    def _determine_relevance(self, doc: Dict[str, Any], source: ErasmusCrawlSource) -> List[str]:
        """
        Determine what aspects of Erasmus+ project development this document is relevant for.
        """
        content = doc.get("content", "").lower()
        title = doc.get("title", "").lower()
        
        relevance = []
        
        # Check for different project phases
        if any(term in content or term in title for term in [
            "brainstorm", "idea", "concept", "innovation", "creative"
        ]):
            relevance.append("brainstorming")
            
        if any(term in content or term in title for term in [
            "plan", "structure", "timeline", "milestone", "objective"
        ]):
            relevance.append("planning")
            
        if any(term in content or term in title for term in [
            "application", "proposal", "submission", "form", "template"
        ]):
            relevance.append("application_writing")
            
        if any(term in content or term in title for term in [
            "partner", "consortium", "cooperation", "network"
        ]):
            relevance.append("partner_search")
            
        # Check for focus areas
        focus_areas_mapping = {
            "digital": ["digital", "technology", "ict", "online", "virtual"],
            "environment": ["environment", "green", "climate", "sustainability"],
            "inclusion": ["inclusion", "diversity", "accessibility", "equality"],
            "youth": ["youth", "young people", "students"],
            "education": ["education", "training", "learning", "pedagogy"]
        }
        
        for focus_area, keywords in focus_areas_mapping.items():
            if any(keyword in content or keyword in title for keyword in keywords):
                relevance.append(f"focus_{focus_area}")
        
        return relevance

    def _filter_sources_by_focus(self, focus_areas: List[str]) -> List[ErasmusCrawlSource]:
        """Filter crawling sources based on focus areas."""
        # This could be enhanced to dynamically prioritize sources
        # based on the focus areas the user is interested in
        return self.erasmus_sources

    async def update_knowledge_base(self, max_age_days: int = 7) -> Dict[str, Any]:
        """
        Update the knowledge base by re-crawling sources that haven't been updated recently.
        
        Args:
            max_age_days: Maximum age in days before a source should be re-crawled
        """
        sources_to_update = []
        
        for source in self.erasmus_sources:
            # Check if source needs updating based on its frequency and last update
            if await self._needs_update(source, max_age_days):
                sources_to_update.append(source)

        if not sources_to_update:
            return {"message": "Knowledge base is up to date", "sources_updated": 0}

        # Crawl sources that need updating
        update_results = {"sources_updated": 0, "errors": []}
        
        for source in sources_to_update:
            try:
                await self._crawl_erasmus_source(source, update_results)
                update_results["sources_updated"] += 1
            except Exception as e:
                update_results["errors"].append({
                    "source": source.url,
                    "error": str(e)
                })

        return update_results

    async def _needs_update(self, source: ErasmusCrawlSource, max_age_days: int) -> bool:
        """Check if a source needs to be re-crawled."""
        # This would check the last update timestamp from the database
        # For now, we'll use the source's update frequency
        return True  # Simplified - always update for demo

    async def search_erasmus_knowledge(self, query: str, source_types: List[str] = None) -> Dict[str, Any]:
        """
        Search the Erasmus+ knowledge base for specific information.
        
        Args:
            query: Search query
            source_types: Optional filter by source types
        
        Returns:
            Search results with relevance scoring
        """
        # This would integrate with the RAG service for semantic search
        # For now, return a placeholder structure
        return {
            "query": query,
            "results": [],
            "source_types_searched": source_types or ["all"],
            "total_results": 0
        }