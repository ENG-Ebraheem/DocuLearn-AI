from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRESENTATION_ROOT = PROJECT_ROOT / "app" / "presentation"


def test_main_is_a_small_application_shell():
    main_source = (PROJECT_ROOT / "app" / "main.py").read_text(encoding="utf-8")
    assert len(main_source.splitlines()) < 100
    assert "create_platform_service" in main_source
    assert "PAGE_RENDERERS" in main_source
    assert "FAISSVectorStore" not in main_source
    assert "SentenceTransformerEmbeddingProvider" not in main_source
    assert "DocumentRepositoryImpl" not in main_source


def test_presentation_pages_do_not_depend_on_infrastructure_directly():
    page_files = list((PRESENTATION_ROOT / "pages").glob("*.py"))
    assert page_files
    for path in page_files:
        source = path.read_text(encoding="utf-8")
        assert "app.infrastructure" not in source, path.name
        assert "sqlalchemy" not in source.lower(), path.name
        assert "FAISSVectorStore" not in source, path.name
        assert "SentenceTransformer" not in source, path.name


def test_presentation_structure_contains_pages_components_state_and_navigation():
    for directory in ("pages", "components", "state", "navigation", "styles"):
        assert (PRESENTATION_ROOT / directory).is_dir()


def test_document_scoped_widget_key_conventions_are_present():
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PRESENTATION_ROOT / "components").glob("*.py")
    )
    assert "document_id" in sources
    assert "generate_summary_{document_id}" in sources
    assert "document_chat_input_{document_id}" in (
        PRESENTATION_ROOT / "pages" / "chat.py"
    ).read_text(encoding="utf-8")
