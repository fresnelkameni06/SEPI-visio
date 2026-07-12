import streamlit as st
from streamlit_extras.mention import mention
from streamlit_extras.avatar import avatar


def show():
    st.markdown("""
    <style>

    .block-container{
        padding-top:2rem;
        padding-bottom:3rem;
    }

    .hero-card{
        padding:1.6rem;
        border-radius:18px;
        border:1px solid rgba(0,0,0,.08);
        background:linear-gradient(
            135deg,
            rgba(0,104,116,.08),
            rgba(2,171,146,.05)
        );
    }

    .section-card{
        padding:1.2rem;
        border-radius:15px;
        border:1px solid rgba(0,0,0,.08);
        background:transparent;
    }

    .small-muted{
        color:#6b7280;
    }

    ul.clean-list{
        padding-left:20px;
    }

    ul.clean-list li{
        margin-bottom:.45rem;
    }

    </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("À propos du projet")
    st.caption("Wild Dump Prevention — Web App de suivi de l’état des poubelles par image")

    with st.container():
        st.markdown("""
        <div class="hero-card">

        <h2>
        Prévenir les dépôts sauvages grâce à une approche simple,
        utile et frugale
        </h2>

        <p>
        Ce projet vise à détecter automatiquement l'état des poubelles
        publiques à partir d'images afin d'anticiper les débordements,
        améliorer la gestion urbaine et limiter les dépôts sauvages.
        </p>

        <p class="small-muted">
        Le projet repose sur l'acquisition d'images, leur annotation,
        l'extraction de caractéristiques visuelles,
        une classification simple et un tableau de bord de suivi.
        </p>

        </div>
        """, unsafe_allow_html=True)

    st.markdown("""<div><br><br></div>""", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Collecte", "Images terrain")
    c2.metric("Analyse", "Features simples")
    c3.metric("Décision", "Règles conditionnelles")
    c4.metric("Impact", "Prévention & sobriété")

    st.divider()

    # Contexte / Objectifs
    left, right = st.columns([1.4, 1])

    with left:
        st.subheader("Contexte")
        st.markdown("""
        Le projet répond à un manque de suivi en temps réel de l'état des
        infrastructures de collecte.

        Lorsqu'une poubelle déborde sans être détectée rapidement,
        les déchets s'accumulent et favorisent l'apparition de dépôts sauvages.

        L'objectif est donc de proposer une solution simple permettant :
        - de détecter les poubelles pleines ;
        - de centraliser les images ;
        - de cartographier les zones à risque ;
        - d'aider les collectivités à planifier leurs interventions.""")

    with right:
        st.subheader("Objectifs")
        st.markdown("""
    <div class="section-card">
    <ul class="clean-list">
    <li>Collecter des images via agents ou caméras.</li>
    <li>Permettre une annotation simple des images.</li>
    <li>Extraire automatiquement des caractéristiques visuelles.</li>
    <li>Appliquer une logique de classification sans modèle complexe.</li>
    <li>Afficher des statistiques et visualisations d’aide à la décision.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Diagramme architecture
    st.subheader("Architecture fonctionnelle")

    architecture = """
    digraph G {
        rankdir=LR;
        bgcolor="transparent";
        graph [
            fontname="Helvetica"];
        node [
            shape=box,
            style="rounded,filled",
            fillcolor="white",
            color="#008080",
            fontname="Helvetica",
            fontsize=11];
        edge [
            color="#008080",
            arrowsize=0.8];
        collecte [label="Collecte\nd'images"];
        upload [label="Upload sur l'App"];
        stockage [label="Stockage\nimages + métadonnées"];
        annotation [label="Annotation\nmanuelle"];
        extraction [label="Extraction\ndes caractéristiques"];
        regles [label="Règles de\nclassification"];
        bdd [label="Base de données"];
        dashboard [label="Dashboard + Statistiques"];
        carto [label="Zones à risque"];
        decision [label="Aide à la décision"];
        collecte -> upload;
        upload -> stockage;
        stockage -> annotation;
        stockage -> extraction;
        extraction -> regles;
        annotation -> bdd;
        regles -> bdd;
        bdd -> dashboard;
        bdd -> carto;
        dashboard -> decision;
        carto -> decision;}
    """

    st.graphviz_chart(architecture, width="stretch")

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
    <div class="section-card">

    ### Chaîne de traitement

    - Upload et stockage des images
    - Annotation pleine / vide
    - Extraction des caractéristiques visuelles
    - Classification par règles conditionnelles
    - Restitution dans un tableau de bord

    </div>
    """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
    <div class="section-card">

    ### Technologies

    - Web App : Streamlit
    - Base de données : SQLite
    - Traitement image : Pillow / OpenCV
    - Visualisation : Streamlit / Matplotlib

    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Avatars
    st.subheader("L’équipe projet")

    col1, col2, col3 = st.columns(3)
    with col1:
        avatar(
            "static/Mathieu.jpeg",
            label="Mathieu Chabrun",
            caption="Chef d’équipe, Model IA",)
    with col2:
        avatar(
            "static/ArthurDo.jpg",
            label="Arthur Donnat",
            caption="Web App",)
    with col3:
        avatar(
            "static/Enzo.jpg",
            label="Enzo Carreiras",
            caption="Visualisations",)
    co1, co2, co3 = st.columns(3)
    with co1:
        avatar(
            "static/ArthurDe.jpg",
            label="Arthur Delannoy",
            caption="Extraction des features",)

    st.divider()

    # Sobriété numérique
    st.subheader("Écoconception")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
    <div class="section-card">
    <h4>Principes RGESN à valoriser</h4>
    <ul class="clean-list">
    <li>Questionner l’utilité réelle du service.</li>
    <li>Définir clairement les cibles et besoins utilisateurs.</li>
    <li>Limiter le poids des interfaces et des médias.</li>
    <li>Réduire les requêtes, optimiser le cache et la compression.</li>
    <li>Choisir des architectures et hébergements cohérents.</li>
    <li>Adapter la complexité algorithmique au besoin réel.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
    <div class="section-card">
    <h4>Axes d’amélioration projet</h4>
    <ul class="clean-list">
    <li>Compresser et redimensionner les images à l’upload.</li>
    <li>Prévoir suppression / archivage des données obsolètes.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # Diagramme impacts / risques
    st.subheader("Risques et vigilance")

    risk_mermaid = """
    mindmap
      root((Projet))
        Risques techniques
          Qualité des images
          Lenteur serveur
          Dépendances externes
          Données incomplètes
        Risques d'usage
          Erreurs d'annotation
          Prise en main hétérogène
        Impacts environnementaux
          Stockage
          Transfert de données
          Poids de l'interface
          Hébergement
          Complexité algorithmique
    """

    try:
        st.iframe(f"""
        <pre class="mermaid">
        {risk_mermaid}
        </pre>
        <script type="module">
          import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
          mermaid.initialize({{ startOnLoad: true }});
        </script>
        """, height=420)
    except Exception:
        st.code(risk_mermaid, language="mermaid")

    r1, r2 = st.columns(2)

    with r1:
        st.markdown("""
    - **Qualité des images** : prévoir prévisualisation, contrôle minimal et guide d’upload.
    - **Règles de classification** : offrir un mécanisme simple de test et d’ajustement.
    - **Performance** : optimiser stockage, traitement et compression.
    - **Données incomplètes** : imposer certains champs et simplifier la saisie.
    """)

    with r2:
        st.markdown("""
    - **Compétences variables des équipes** : fournir starter kit, documentation et tutoriels.
    - **Erreurs d’annotation** : ajouter confirmation, annulation et édition.
    - **Dépendances externes** : figer les versions critiques.
    - **Impacts numériques** : surveiller poids des médias, requêtes et hébergement.
    """)

    st.divider()

    # Mentions
    st.subheader("Mentions")

    st.markdown("Exemple d’utilisation des mentions pour signaler des références ou des briques projet :")

    mention(
        label="RGESN",
        icon="🌱",
        url="https://ecoresponsable.numerique.gouv.fr/publications/referentiel-general-ecoconception/"
    )

    mention(
        label="Streamlit",
        icon="🧭",
        url="https://streamlit.io/"
    )
