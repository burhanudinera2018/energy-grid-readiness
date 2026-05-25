# dashboard/footer.py
import streamlit as st

def show_footer(custom_text=None):
    """Menampilkan footer copyright di semua halaman"""
    
    default_text = "Portfolio Project Energy 2026"
    display_text = custom_text if custom_text else default_text
    
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;">
            <p style="margin: 0; color: #1f1f1f;">
                © 2026 <strong>Burhanudin Badiuzaman</strong> - {display_text}
            </p>
            <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">
                Data sources: Global Power Plant Database | Global Transmission Database | RUPTL PLN
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )