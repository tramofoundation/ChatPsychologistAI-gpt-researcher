from graphrag_extra.query.structured_search.global_search.search import GlobalExtract
from graphrag.config.models.graph_rag_config import GraphRagConfig
from graphrag.model.community_report import CommunityReport
from graphrag.model.entity import Entity
from graphrag.model.community import Community

def get_global_extract_engine(
    config: GraphRagConfig,
    reports: list[CommunityReport],
    entities: list[Entity],
    communities: list[Community],
    response_type: str,
    dynamic_community_selection: bool = False,
    map_system_prompt: str | None = None,
    reduce_system_prompt: str | None = None,
    general_knowledge_inclusion_prompt: str | None = None,
) -> GlobalExtract:
    from graphrag import query
    query.factories.GlobalSearch = GlobalExtract

    return query.factories.get_global_search_engine(
        config,
        reports,
        entities,
        communities,
        response_type,
        dynamic_community_selection,
        map_system_prompt,
        reduce_system_prompt,
        general_knowledge_inclusion_prompt
    )
