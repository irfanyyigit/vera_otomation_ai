import streamlit as st
import os
from db.database import get_db

def render_support(role, username):
    conn = get_db()
    c = conn.cursor()

    # ---------------- USER ----------------
    if role == "user":
        st.header("Teknik Destek Talebi")

        with st.form("talep_form", clear_on_submit=True):
            mesaj = st.text_area("Sorununuz:")
            foto = st.file_uploader("Ekran görüntüsü", type=["jpg", "png"])

            if st.form_submit_button("Gönder"):
                foto_yolu = None

                if foto:
                    if not os.path.exists("uploads"):
                        os.makedirs("uploads")

                    foto_yolu = f"uploads/{foto.name}"
                    with open(foto_yolu, "wb") as f:
                        f.write(foto.getbuffer())

                # username artık doğru geliyor
                c.execute(
                    "INSERT INTO talepler (username, mesaj, foto_yolu) VALUES (?, ?, ?)",
                    (username, mesaj, foto_yolu)
                )
                conn.commit()

                st.success("Talep gönderildi!")

    # ---------------- ADMIN ----------------
    elif role == "admin":
        st.header("Gelen Talepler")

        c.execute("SELECT * FROM talepler ORDER BY tarih DESC")
        talepler = c.fetchall()

        if not talepler:
            st.info("Henüz talep yok.")

        for t in talepler:
            talep_id = t[0]

            with st.expander(f"Talep #{talep_id} - {t[4]}"):
                st.write(f"**Kullanıcı:** {t[1]}")
                st.write(f"**Mesaj:** {t[2]}")

                if t[3] and os.path.exists(t[3]):
                    st.image(t[3])

                # UNIQUE BUTTON KEY (çok önemli)
                if st.button("Sil", key=f"delete_{talep_id}"):

                    # dosyayı sil
                    if t[3] and os.path.exists(t[3]):
                        os.remove(t[3])

                    # db'den sil
                    c.execute("DELETE FROM talepler WHERE id=?", (talep_id,))
                    conn.commit()

                    st.success("Talep silindi")
                    st.rerun()

    conn.close()