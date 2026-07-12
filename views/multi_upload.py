from datetime import datetime
import os
import streamlit as st

import database as db
from classifier import analyse_image
from features_extraction import arthur_extract_features


DATA_FOLDER = "Data/web_app"


def init_state():
    if "images_queue" not in st.session_state:
        st.session_state.images_queue = []
    if "index" not in st.session_state:
        st.session_state.index = 0
    if "left_stack" not in st.session_state:
        st.session_state.left_stack = []   # Vide
    if "right_stack" not in st.session_state:
        st.session_state.right_stack = []  # Pleine
    if 'disabled' not in st.session_state:
        st.session_state.disabled = False
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    if "mu_started" not in st.session_state:
        st.session_state.mu_started = False


def reset_state():
    if st.session_state.images_queue:
        st.session_state.images_queue = []
        st.session_state.index = 0
        st.session_state.left_stack = []
        st.session_state.right_stack = []
    st.session_state.other_p = False
    st.session_state.disabled = False
    st.session_state.uploader_key += 1

    st.session_state.mu_started = False


def save_annotation(annot, hsh, fpath):
    """
    Fonction callback pour enregistrer l'annotation.
    """
    db.update_manual_annotation(annot, hsh)
    if annot == "Vide":
        st.session_state.left_stack.append(fpath)
    else:
        st.session_state.right_stack.append(fpath)

    st.session_state.index += 1


def _process_current():
    """
    Traite l'image courante : sauvegarde + features + classification.
    Retourne (filepath, hash).
    """
    current_file = st.session_state.images_queue[st.session_state.index]

    initial_filename = current_file.name
    extension = '.' + initial_filename.split(".")[-1]

    # File naming convention : Source_Type_Timestamp_Code ; code: to avoid collision just in case.
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    new_filename = f"App_Annoté_{timestamp}"

    filepath = os.path.join(DATA_FOLDER, new_filename + "_1" + extension)
    k = 2
    while os.path.exists(filepath):
        filepath = os.path.join(DATA_FOLDER, new_filename + '_' + str(k) + extension)
        k += 1

    img_hash = db.compute_uploaded_file_hash(current_file)

    if db.image_hash_exists(img_hash):
        st.warning(f"Cette image est déjà présente dans la database\n - vous **devez** cependant la réannoter.")
        return db.get_filepath_from_hash(img_hash), img_hash

    with open(filepath, "wb") as f:
        f.write(current_file.getbuffer())

    feats, ai_annotation, ai_confidence, ai_score = analyse_image(filepath)
    a_features = arthur_extract_features(filepath)

    db.insert_image((
        initial_filename,
        new_filename + '_' + str(k - 1) + extension,
        img_hash,
        filepath,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        None,  # manual_annotation
        ai_annotation,  # Vide / Pleine
        ai_confidence,  # %
        ai_score,  # 0-5
        a_features["file_size"],
        a_features["width"], a_features["height"],
        feats["aspect_ratio"],
        a_features["avg_r"], a_features["avg_g"], a_features["avg_b"],
        a_features["min_r"], a_features["min_g"], a_features["min_b"],
        a_features["max_r"], a_features["max_g"], a_features["max_b"],
        a_features["avg_l"],
        feats["brightness"],
        a_features["contrast"],
        feats["saturation"], feats["colorfulness"],
        feats["dark_ratio"], feats["edge_density"], feats["texture"],
        feats["entropy"], feats["green_ratio"], feats["sharpness"],
        feats["max_zone_edges"], feats["zone_variance"], feats["bottom_edge_density"],
        feats["ground_clutter"], feats["green_zone_max"], feats["green_zone_var"],
        str(a_features["r_histogram"]), str(a_features["g_histogram"]), str(a_features["b_histogram"]),
        str(a_features["l_histogram"]), str(a_features["hue_histogram"]),
        str(a_features["bin_r_histogram"]), str(a_features["bin_g_histogram"]), str(a_features["bin_b_histogram"]),
        str(a_features["bin_hue_histogram"])
    ))
    return filepath, img_hash


def show():
    init_state()
    if st.session_state.other_p:
        reset_state()

    left_col, center_col, right_col = st.columns([2, 18, 2])
    with left_col:
        st.markdown("### 🟢 Vide")
        for img in st.session_state.left_stack[-8:]:
            st.image(img)
    with right_col:
        st.markdown("### 🔴 Pleine")
        for img in st.session_state.right_stack[-8:]:
            st.image(img)

    with center_col:
        st.title("Multi-Upload")
        st.subheader("Uploader plusieurs images. Elles seront analysées une par une.")

        st.markdown("<div><br></div>", unsafe_allow_html=True)

        # Dépôt des images
        uploaded_files = st.file_uploader(
            "Déposer plusieurs images", type=["jpg", "jpeg", "png"],
            accept_multiple_files=True, disabled=st.session_state.disabled,
            key=f"uploader_{st.session_state.uploader_key}")

        if uploaded_files and not st.session_state.images_queue:
            for f in uploaded_files:
                st.session_state.images_queue.append(f)

        # Bouton Prédire (démarre le traitement séquentiel)
        if st.session_state.images_queue and not st.session_state.mu_started:
            st.info(f"{len(st.session_state.images_queue)} image(s) prête(s).")
            if st.button("Analyser", type="primary"):
                st.session_state.mu_started = True
                st.session_state.index = 0
                st.rerun()

        # Traitement image par image
        if st.session_state.mu_started and st.session_state.index < len(st.session_state.images_queue):
            st.session_state.disabled = True

            total = len(st.session_state.images_queue)
            idx = st.session_state.index
            st.progress(idx / total, text=f"Image {idx + 1} / {total}")

            filepath, img_hash = _process_current()

            data = db.get_data_from_hash(img_hash)
            ai_annotation = data[7]
            ai_confidence = data[8]

            c1, c2, c3 = st.columns([1, 10, 1])
            with c2:
                st.markdown("### Image à annoter")
                st.image(filepath, width="stretch")

                left_col3, center_col3, right_col3 = st.columns(3)
                with center_col3:
                    st.markdown("**Annotation manuelle**")
                    b1, b2 = st.columns(2)
                    with b1:
                        st.button("🟢 Vide", shortcut="Left", on_click=save_annotation, args=("Vide", img_hash, filepath))
                    with b2:
                        st.button("🔴 Pleine", shortcut="Right", on_click=save_annotation, args=("Pleine", img_hash, filepath))

                st.markdown("---")

                st.markdown("### Résultat de l'analyse")

                if ai_annotation == "Pleine":
                    st.markdown("<div class='result-full'>🔴 Pleine</div>", unsafe_allow_html=True)
                    st.write("La poubelle est pleine. Intervention recommandée.")
                else:
                    st.markdown("<div class='result-ok'>🟢 Vide</div>", unsafe_allow_html=True)
                    st.write("La poubelle est vide. Aucune action nécessaire.")

                st.metric("Confiance IA", f"{ai_confidence:.0f} %")

        # Fin
        elif st.session_state.mu_started and st.session_state.index >= len(st.session_state.images_queue):
            st.success("Toutes les images ont été traitées et annotées !")
            st.write(f"🟢 Vide : {len(st.session_state.left_stack)}   |   🔴 Pleine : {len(st.session_state.right_stack)}")
            _, middle, _ = st.columns(3)
            with middle:
                st.button("↺ Recommencer", on_click=reset_state)
