"""Library page: upload, organize, find, and open documents."""

from __future__ import annotations

import logging

import streamlit as st

from app.presentation.components.common import empty_state, friendly_error, page_header
from app.presentation.components.document_card import render_document_card
from app.presentation.navigation.router import navigate
from app.presentation.state.session_state import PAGE_LIBRARY

logger = logging.getLogger(__name__)


def render(service) -> None:
    page_header("مكتبتي", "ارفع مستنداتك ونظمها وافتح أي مستند مباشرة.")
    upload_tab, documents_tab, organization_tab = st.tabs(
        ["رفع مستند", "المستندات", "تنظيم المواد"]
    )

    with upload_tab:
        _render_upload(service)
    with documents_tab:
        _render_documents(service)
    with organization_tab:
        _render_courses(service)


def _render_upload(service) -> None:
    courses = service.list_courses()
    course_options = {"بدون مادة": None, **{course.name: course.id for course in courses}}

    with st.form("library_upload_form", border=True, clear_on_submit=True):
        uploaded_file = st.file_uploader(
            "اختر مستندًا",
            type=["pdf", "docx", "xlsx", "txt"],
            help="يمكنك تنظيم المستند ضمن مادة، وهو خيار اختياري.",
        )
        selected_course = st.selectbox("المادة التنظيمية", list(course_options), key="library_upload_course")
        submitted = st.form_submit_button("رفع وفهرسة المستند", type="primary", icon=":material/upload:")

    if submitted:
        if uploaded_file is None:
            st.warning("اختر ملفًا قبل بدء الرفع.", icon=":material/warning:")
            return
        try:
            with st.status("تجري معالجة المستند…", expanded=True) as status:
                st.write("استخراج النص وتقسيمه إلى أجزاء.")
                result = service.ingest_uploaded_document(
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    course_options[selected_course],
                )
                if result.indexed:
                    status.update(label="تمت فهرسة المستند", state="complete")
                    st.success("أصبح المستند جاهزًا للمحادثة والتعلم.", icon=":material/check_circle:")
                else:
                    status.update(label="تم حفظ المستند دون فهرسة", state="error")
                    st.warning("تعذر استخراج نص كافٍ للفهرسة من هذا المستند.", icon=":material/warning:")
        except ValueError as error:
            st.warning(str(error), icon=":material/warning:")
        except Exception:
            logger.exception("Document ingestion failed")
            friendly_error("تعذر رفع المستند أو فهرسته. تحقق من الملف وحاول مرة أخرى.")


def _render_documents(service) -> None:
    documents = service.list_documents()
    if not documents:
        empty_state(
            "لا توجد مستندات بعد",
            "ابدأ برفع أول مستند، ثم ستتمكن من فتحه أو دراسته أو الدردشة معه.",
        )
        return

    courses = service.list_courses()
    course_options = {"كل المستندات": None, **{course.name: course.id for course in courses}}
    search_col, filter_col, sort_col = st.columns([2, 1, 1])
    search = search_col.text_input("ابحث عن مستند", placeholder="اكتب اسم المستند", key="library_search")
    selected_course = filter_col.selectbox("المادة", list(course_options), key="library_course_filter")
    sort_by = sort_col.selectbox("الترتيب", ["الأحدث", "الأقدم", "الاسم"], key="library_sort")

    if search.strip():
        documents = [document for document in documents if search.strip().lower() in document.name.lower()]
    if course_options[selected_course]:
        documents = [document for document in documents if document.course_id == course_options[selected_course]]

    sort_key = {
        "الأحدث": lambda document: document.created_at,
        "الأقدم": lambda document: document.created_at,
        "الاسم": lambda document: document.name.lower(),
    }[sort_by]
    documents.sort(key=sort_key, reverse=sort_by == "الأحدث")

    if not documents:
        st.info("لا توجد نتائج مطابقة للبحث أو الفلترة.", icon=":material/search_off:")
        return

    for document in documents:
        render_document_card(service, document, key_prefix="library")
        _render_delete_action(service, document)


def _render_delete_action(service, document) -> None:
    with st.popover("حذف", icon=":material/delete:"):
        st.warning(f"سيُحذف المستند «{document.name}» مع محتوى التعلم والمحادثة المرتبط به.")
        if st.button("تأكيد الحذف", key=f"library_confirm_delete_{document.id}", type="primary", icon=":material/delete_forever:"):
            try:
                service.delete_document(document.id)
                if st.session_state.get("active_document_id") == document.id:
                    st.session_state["active_document_id"] = None
                st.toast("تم حذف المستند.", icon=":material/check_circle:")
                navigate(PAGE_LIBRARY, remember_current_page=False)
            except Exception:
                logger.exception("Document deletion failed")
                friendly_error("تعذر حذف المستند. حاول مرة أخرى.")


def _render_courses(service) -> None:
    st.caption("المواد وسيلة تنظيم اختيارية. لا تحتاج إليها لفتح أي مستند أو دراسته.")
    with st.form("create_course_form", border=True, clear_on_submit=True):
        name = st.text_input("اسم المادة", placeholder="مثل: برمجة بايثون")
        submitted = st.form_submit_button("إضافة مادة", type="primary", icon=":material/add:")
    if submitted:
        try:
            service.create_course(name)
            st.toast("تمت إضافة المادة.", icon=":material/check_circle:")
            st.rerun()
        except ValueError as error:
            st.warning(str(error), icon=":material/warning:")
        except Exception:
            logger.exception("Course creation failed")
            friendly_error("تعذر إنشاء المادة. حاول مرة أخرى.")

    courses = service.list_courses()
    if not courses:
        st.caption("لا توجد مواد تنظيمية بعد.")
        return
    for course in courses:
        documents_count = len([doc for doc in service.list_documents() if doc.course_id == course.id])
        with st.container(border=True):
            st.markdown(f"#### {course.name}")
            st.caption(f"{documents_count} مستند")
            with st.popover("حذف المادة", icon=":material/delete:"):
                st.warning("سيتم إزالة المادة وتصبح المستندات المرتبطة بها غير مخصصة مادة دون حذف المستندات نفسها.")
                if st.button("تأكيد حذف المادة", key=f"confirm_course_delete_{course.id}", type="primary"):
                    try:
                        service.delete_course(course.id)
                        st.rerun()
                    except Exception:
                        logger.exception("Course deletion failed")
                        friendly_error("تعذر حذف المادة. حاول مرة أخرى.")
