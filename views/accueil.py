from datetime import datetime
import os
import streamlit as st

import database as db
from classifier import analyse_image
from features_extraction import arthur_extract_features


DATA_FOLDER = "Data/web_app"


def show():
    left_col, center_col, right_col = st.columns([1, 10, 1])
    with center_col:
        st.title("Web App VISIO - Wild Dump Prevention")
        st.subheader("Détection de l'état des poubelles")

        st.markdown("""
            <div class='green-title'>
            Une ville plus propre, des déchets mieux gérés.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""<div><br></div>""", unsafe_allow_html=True)

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("### Déposer une image de poubelle")
            uploaded_file = st.file_uploader("Formats acceptés : JPG, PNG, JPEG", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            initial_filename = uploaded_file.name
            extension = '.' + initial_filename.split(".")[-1]

            # File naming convention : Source_Type_Timestamp_Code ; code: to avoid collision just in case.
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            new_filename = f"App_Annoté_{timestamp}"

            filepath = os.path.join(DATA_FOLDER, new_filename + "_1" + extension)
            k = 2
            while os.path.exists(filepath):
                filepath = os.path.join(DATA_FOLDER, new_filename + '_' + str(k) + extension)
                k += 1

            img_hash = db.compute_uploaded_file_hash(uploaded_file)
            annotation = None

            if db.image_hash_exists(img_hash):
                with col_left:
                    st.info("Cette image est déjà présente dans la database\n - vous pouvez cependant la réannoter.")
                filepath = db.get_filepath_from_hash(img_hash)
            else:
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                with col_left:
                    st.success("Image enregistrée.")
                    st.info("Image en cours d'analyse - veuillez patienter.")

                feats, ai_annotation, ai_confidence, ai_score = analyse_image(filepath)
                a_features = arthur_extract_features(filepath)

                db.insert_image((
                    initial_filename,
                    new_filename + '_' + str(k - 1) + extension,
                    img_hash,
                    filepath,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    annotation,  # manual_annotation
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

                with col_left:
                    st.success("Analyse terminée.")

            with col_left:
                st.markdown("**Image sélectionnée :**")
                st.image(filepath, width="stretch")

            with col_right:
                left_col3, center_col3, right_col3 = st.columns([1, 10, 1])
                with center_col3:
                    st.markdown("**Annotation manuelle**")
                    c1, c2 = st.columns(2)
                    annotation = None
                    with c1:
                        if st.button("🟢 Vide", shortcut="Left"):
                            annotation = "Vide"
                    with c2:
                        if st.button("🔴 Pleine", shortcut="Right"):
                            annotation = "Pleine"

                if annotation:
                    db.update_manual_annotation(annotation, img_hash)
                    st.success(f"Annotation '{annotation}' enregistrée.")

                data = db.get_data_from_hash(img_hash)
                (id_, image_hash, filename, initial_filename, filepath, upload_date,
                 manual_annotation, ai_annotation, ai_confidence, ai_score,
                 file_size, width, height, aspect_ratio,
                 avg_r, avg_g, avg_b,
                 min_r, min_g, min_b,
                 max_r, max_g, max_b,
                 avg_l,
                 brightness, contrast, saturation, colorfulness,
                 dark_ratio, edge_density, texture, entropy, green_ratio, sharpness,
                 max_zone_edges, zone_variance, bottom_edge_density, ground_clutter,
                 green_zone_max, green_zone_var,
                 histogram_r, histogram_g, histogram_b, histogram_l, hue_histogram,
                 bin_histogram_r, bin_histogram_g, bin_histogram_b, bin_hue_histogram,) = data

                st.markdown("---")

                st.markdown("### Résultat de l'analyse")
                if ai_annotation == "Pleine":
                    st.markdown(f"<div class='result-full'>🔴 Pleine</div>", unsafe_allow_html=True)
                    st.write("La poubelle est pleine. Une intervention est recommandée.")
                else:
                    st.markdown(f"<div class='result-ok'>🟢 Vide</div>", unsafe_allow_html=True)
                    st.write("La poubelle est vide. Aucune action nécessaire.")

                st.metric("Confiance IA", f"{ai_confidence:.0f} %")

                st.markdown("### Détails complet de l'image")
                with st.expander("Général"):
                    st.write("ID :", id_)
                    st.write("Hash :", image_hash)
                    st.write("Nom du fichier :", filename)
                    st.write("Nom d'origine du fichier :", initial_filename)
                    st.write("Chemin d'accès du fichier :", filepath)
                    st.write("Date d'upload :", upload_date)
                    st.write("Taille du fichier :", f"{file_size} bytes")
                    st.write("Dimension de l'image :", f"{width} x {height}")
                with st.expander("Annotations", expanded=True):
                    st.write("Annotation manuelle :", manual_annotation)
                    st.write("Annotation IA :", ai_annotation)
                    st.write("Confiance IA :", ai_confidence)
                    st.write("Score IA :", ai_score)
                with st.expander("RGB"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Rouge Moyen :", avg_r)
                    col2.metric("Vert Moyen :", avg_g)
                    col3.metric("Bleu Moyen :", avg_b)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Rouge Min", min_r)
                    col2.metric("Vert Min :", min_g)
                    col3.metric("Bleu Min :", min_b)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Rouge Max :", max_r)
                    col2.metric("Vert Max :", max_g)
                    col3.metric("Bleu Max :", max_b)
                with st.expander("Luminance"):
                    st.metric("Moyenne :", avg_l)
                    st.metric("Contraste :", contrast)
                with st.expander("Autres"):
                    st.metric("Luminosité :", brightness)
                    st.metric("Saturation :", saturation)
                    st.metric("Colorfulness :", colorfulness)
                    st.metric("Dark ratio :", dark_ratio)
                    st.metric("Edge density :", edge_density)
                    st.metric("Texture :", texture)
                    st.metric("Entropy :", entropy)
                    st.metric("Green ratio :", green_ratio)
                    st.metric("Sharpness :", sharpness)
                    st.metric("max_zone_edges :", max_zone_edges)
                    st.metric("zone_variance :", zone_variance)
                    st.metric("bottom_edge_density :", bottom_edge_density)
                    st.metric("ground_clutter :", ground_clutter)
                    st.metric("green_zone_max :", green_zone_max)
                    st.metric("green_zone_variance :", green_zone_var)
                with st.expander("Histogrammes"):
                    st.write("Rouge :", histogram_r)
                    st.write("Vert :", histogram_g)
                    st.write("Bleu :", histogram_b)
                    st.write("Luminance :", histogram_l)
                    st.write("Teinte :", hue_histogram)
                    st.write("Poubelle - Rouge :", bin_histogram_r)
                    st.write("Poubelle - Vert :", bin_histogram_g)
                    st.write("Poubelle - Bleu :", bin_histogram_b)
                    st.write("Poubelle - Teinte :", bin_hue_histogram)
