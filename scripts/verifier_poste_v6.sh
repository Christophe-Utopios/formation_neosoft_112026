#!/usr/bin/env bash
# Vérification et préparation du poste stagiaire — NSS+ J01
#
# Usage :
#   bash verifier_poste_v6.sh [--sans-reseau] [--sans-installation]
#
# À lancer depuis la racine du dépôt NeoFlow.
#
# Installe automatiquement les outils de développement manquants :
# git, Java 21, Maven, Node.js/npm, Python 3.11+ et uv.
#
# OpenCode 2.x est obligatoire, mais son installation reste manuelle.
#
# --sans-installation : vérifie seulement, n'installe rien.
# --sans-reseau      : désactive les contrôles réseau et les installations.
#
# N'affiche jamais la clé API.
# Aucun appel de génération : l'API Anthropic est testée sur /v1/models.

set -u

SANS_RESEAU=0
INSTALLATION=1

for arg in "$@"; do
  case "$arg" in
    --sans-reseau)
      SANS_RESEAU=1
      INSTALLATION=0
      ;;
    --sans-installation)
      INSTALLATION=0
      ;;
    *)
      printf 'Option inconnue : %s\n' "$arg"
      printf 'Usage : bash %s [--sans-reseau] [--sans-installation]\n' "$0"
      exit 2
      ;;
  esac
done

KO=0
WARN=0

ok() {
  printf '  \033[32mOK\033[0m    %s\n' "$1"
}

warn() {
  printf '  \033[33mWARN\033[0m  %s\n' "$1"
  WARN=$((WARN + 1))
}

ko() {
  printf '  \033[31mKO\033[0m    %s\n' "$1"
  KO=$((KO + 1))
}

info() {
  printf '  \033[36mINFO\033[0m  %s\n' "$1"
}

titre() {
  printf '\n\033[1m%s\033[0m\n' "$1"
}

majeur() {
  printf '%s' "$1" |
    sed -E 's/^v//; s/^1\.([0-9]+).*/\1/; s/^([0-9]+).*/\1/'
}

# ---------------------------------------------------------------------------
# Gestionnaires de paquets
# ---------------------------------------------------------------------------

PM=""

detecter_pm() {
  if command -v brew >/dev/null 2>&1; then
    PM=brew
  elif command -v apt-get >/dev/null 2>&1; then
    PM=apt
  elif command -v dnf >/dev/null 2>&1; then
    PM=dnf
  elif command -v winget >/dev/null 2>&1 ||
       command -v winget.exe >/dev/null 2>&1; then
    PM=winget
  else
    PM=""
  fi
}

SUDO=""

if [ "$(id -u 2>/dev/null || echo 1)" -ne 0 ] &&
   command -v sudo >/dev/null 2>&1; then
  SUDO="sudo"
fi

APT_MAJ=0

apt_maj() {
  if [ "$APT_MAJ" -eq 0 ]; then
    $SUDO apt-get update -y || return 1
    APT_MAJ=1
  fi
}

WINGET_FAIT=0

winget_installer() {
  local w=winget

  command -v winget >/dev/null 2>&1 || w=winget.exe

  if "$w" install -e --id "$1" \
    --accept-source-agreements \
    --accept-package-agreements; then
    WINGET_FAIT=1
  else
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Maven sous Windows
# ---------------------------------------------------------------------------

MAVEN_VERSION="3.9.9"

installer_maven_archive() {
  local dest="$HOME/tools"
  local zip="$HOME/tools/apache-maven-$MAVEN_VERSION-bin.zip"
  local bin="$HOME/tools/apache-maven-$MAVEN_VERSION/bin"

  mkdir -p "$dest" || return 1

  curl -fL --retry 2 -o "$zip" \
    "https://archive.apache.org/dist/maven/maven-3/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.zip" ||
    return 1

  if command -v unzip >/dev/null 2>&1; then
    unzip -q -o "$zip" -d "$dest" || return 1
  elif command -v powershell.exe >/dev/null 2>&1 &&
       command -v cygpath >/dev/null 2>&1; then
    # Les chemins passent par les variables d'environnement pour éviter
    # de les interpoler dans du code PowerShell.
    VERIFIER_MAVEN_ZIP="$(cygpath -w "$zip")" \
    VERIFIER_MAVEN_DEST="$(cygpath -w "$dest")" \
      powershell.exe -NoProfile -Command \
      'Expand-Archive -Force -LiteralPath $env:VERIFIER_MAVEN_ZIP -DestinationPath $env:VERIFIER_MAVEN_DEST' ||
      return 1
  else
    warn "Extraction Maven impossible : unzip ou PowerShell/cygpath requis"
    return 1
  fi

  rm -f "$zip"

  PATH="$bin:$PATH"
  export PATH

  if ! grep -qs "apache-maven-$MAVEN_VERSION/bin" "$HOME/.bashrc"; then
    printf '\n# Maven (verifier_poste)\nexport PATH="$HOME/tools/apache-maven-%s/bin:$PATH"\n' \
      "$MAVEN_VERSION" >> "$HOME/.bashrc"
  fi

  if [ -f "$HOME/.bash_profile" ] &&
     ! grep -qs 'bashrc' "$HOME/.bash_profile"; then
    printf '\n[ -f ~/.bashrc ] && . ~/.bashrc\n' >> "$HOME/.bash_profile"
  fi

  if command -v powershell.exe >/dev/null 2>&1 &&
     command -v cygpath >/dev/null 2>&1; then
    VERIFIER_MAVEN_BIN="$(cygpath -w "$bin")" \
      powershell.exe -NoProfile -Command '
        $d = $env:VERIFIER_MAVEN_BIN
        $p = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($null -eq $p) { $p = "" }
        if (-not ($p.Split(";") -contains $d)) {
          $nouveau = ($p.TrimEnd(";") + ";" + $d).TrimStart(";")
          [Environment]::SetEnvironmentVariable("Path", $nouveau, "User")
        }
      ' ||
      warn "PATH Windows non mis à jour : ajouter le dossier bin de Maven au PATH utilisateur"
  fi
}

# ---------------------------------------------------------------------------
# PATH de la session
# ---------------------------------------------------------------------------

LOCAL_APPDATA="$HOME/AppData/Local"

if [ -n "${LOCALAPPDATA:-}" ] &&
   command -v cygpath >/dev/null 2>&1; then
  LOCAL_APPDATA=$(cygpath -u "$LOCALAPPDATA")
fi

ajouter_au_path() {
  [ -d "$1" ] || return 0

  case ":$PATH:" in
    *":$1:"*) ;;
    *)
      PATH="$1:$PATH"
      export PATH
      ;;
  esac
}

ajouter_chemins_installation() {
  local d

  ajouter_au_path "$HOME/.local/bin"
  ajouter_au_path "$HOME/.cargo/bin"
  ajouter_au_path "$HOME/.opencode/bin"
  ajouter_au_path "$HOME/tools/apache-maven-$MAVEN_VERSION/bin"
  ajouter_au_path "$LOCAL_APPDATA/Microsoft/WinGet/Links"

  for d in "$LOCAL_APPDATA"/Microsoft/WinGet/Packages/astral-sh.uv*; do
    [ -e "$d/uv.exe" ] && ajouter_au_path "$d"
  done

  hash -r 2>/dev/null
}

# ---------------------------------------------------------------------------
# Installation des outils de développement
# ---------------------------------------------------------------------------

installer() {
  [ "$INSTALLATION" -eq 1 ] || return 1

  if [ -z "$PM" ]; then
    warn "Aucun gestionnaire reconnu (brew, apt, dnf, winget) : installer $1 manuellement"
    return 1
  fi

  printf '  \033[36mINST\033[0m  installation de %s via %s...\n' "$1" "$PM"

  local statut=0

  case "$PM:$1" in
    brew:git)
      brew install git || statut=$?
      ;;
    brew:java)
      brew install --cask temurin@21 || statut=$?
      ;;
    brew:maven)
      brew install maven || statut=$?
      ;;
    brew:node)
      brew install node || statut=$?
      ;;
    brew:python)
      brew install python || statut=$?
      ;;
    brew:uv)
      brew install uv || statut=$?
      ;;

    apt:git)
      { apt_maj && $SUDO apt-get install -y git; } || statut=$?
      ;;
    apt:java)
      { apt_maj && $SUDO apt-get install -y openjdk-21-jdk; } || statut=$?
      ;;
    apt:maven)
      { apt_maj && $SUDO apt-get install -y maven; } || statut=$?
      ;;
    apt:node)
      {
        apt_maj &&
          $SUDO apt-get install -y ca-certificates curl &&
          (
            set -o pipefail
            curl -fsSL https://deb.nodesource.com/setup_20.x |
              $SUDO -E bash -
          ) &&
          $SUDO apt-get install -y nodejs
      } || statut=$?
      ;;
    apt:python)
      {
        apt_maj &&
          $SUDO apt-get install -y python3 python3-venv
      } || statut=$?
      ;;

    dnf:git)
      $SUDO dnf install -y git || statut=$?
      ;;
    dnf:java)
      $SUDO dnf install -y java-21-openjdk-devel || statut=$?
      ;;
    dnf:maven)
      $SUDO dnf install -y maven || statut=$?
      ;;
    dnf:node)
      $SUDO dnf install -y nodejs npm || statut=$?
      ;;
    dnf:python)
      $SUDO dnf install -y python3 || statut=$?
      ;;

    winget:git)
      winget_installer Git.Git || statut=$?
      ;;
    winget:java)
      winget_installer EclipseAdoptium.Temurin.21.JDK || statut=$?
      ;;
    winget:maven)
      installer_maven_archive || statut=$?
      ;;
    winget:node)
      winget_installer OpenJS.NodeJS.LTS || statut=$?
      ;;
    winget:python)
      winget_installer Python.Python.3.12 || statut=$?
      ;;

    apt:uv|dnf:uv)
      (
        set -o pipefail
        curl -LsSf https://astral.sh/uv/install.sh | sh
      ) || statut=$?
      ;;
    winget:uv)
      winget_installer astral-sh.uv || statut=$?
      ajouter_chemins_installation

      if ! command -v uv >/dev/null 2>&1; then
        powershell.exe -NoProfile -ExecutionPolicy ByPass -Command \
          "irm https://astral.sh/uv/install.ps1 | iex" ||
          return 1
        statut=0
      fi
      ;;
    *)
      return 1
      ;;
  esac

  ajouter_chemins_installation
  return "$statut"
}

# ---------------------------------------------------------------------------
# Détection des versions
# ---------------------------------------------------------------------------

version_java() {
  java -version 2>&1 | head -1 | sed -E 's/.*"([^"]+)".*/\1/'
}

version_node() {
  node -v 2>/dev/null
}

java_ok() {
  command -v java >/dev/null 2>&1 &&
    [ "$(majeur "$(version_java)")" -ge 21 ] 2>/dev/null
}

node_ok() {
  command -v node >/dev/null 2>&1 &&
    [ "$(majeur "$(version_node)")" -ge 20 ] 2>/dev/null
}

# Sous Windows, python3 peut être un alias Microsoft Store.
# On teste donc réellement chaque interpréteur.

PY=""
PY_TROUVE=""

python_ok() {
  local c d v

  PY=""
  PY_TROUVE=""

  for c in python3 python "py -3"; do
    command -v "${c%% *}" >/dev/null 2>&1 || continue

    # shellcheck disable=SC2086
    v=$($c -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null) ||
      continue

    [ -n "$v" ] || continue
    PY_TROUVE="$c ($v)"

    # shellcheck disable=SC2086
    if $c -c 'import sys;sys.exit(0 if sys.version_info >= (3,11) else 1)' \
      2>/dev/null; then
      PY="$c"
      return 0
    fi
  done

  for d in "$LOCAL_APPDATA"/Programs/Python/Python3*; do
    [ -x "$d/python.exe" ] || continue

    if "$d/python.exe" \
      -c 'import sys;sys.exit(0 if sys.version_info >= (3,11) else 1)' \
      2>/dev/null; then
      PATH="$d:$d/Scripts:$PATH"
      export PATH
      hash -r 2>/dev/null
      PY="$d/python.exe"
      return 0
    fi
  done

  return 1
}

run_py() {
  case "$PY" in
    "py -3") py -3 "$@" ;;
    "") return 127 ;;
    *) "$PY" "$@" ;;
  esac
}

version_python() {
  run_py -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])' 2>/dev/null
}

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

detecter_pm
ajouter_chemins_installation

if [ "$INSTALLATION" -eq 1 ]; then
  if [ -n "$PM" ]; then
    printf '\nInstallation automatique activée (gestionnaire : %s).\n' "$PM"
    printf 'Désactiver avec --sans-installation.\n'
  else
    printf '\nInstallation automatique impossible : aucun gestionnaire reconnu.\n'
  fi
fi

# ---------------------------------------------------------------------------
# 1. Outils de développement
# ---------------------------------------------------------------------------

titre "1. Outils de développement"

command -v git >/dev/null 2>&1 || installer git

if command -v git >/dev/null 2>&1; then
  ok "git $(git --version | awk '{print $3}')"
else
  ko "git absent"
fi

java_ok || installer java

if java_ok; then
  ok "Java $(version_java)"
elif command -v java >/dev/null 2>&1; then
  ko "Java $(version_java) : JDK 21 minimum requis"
  info "Si Java 21 vient d'être installé : rouvrir le terminal ou ajuster JAVA_HOME"
else
  ko "Java absent : JDK 21 requis"
fi

command -v mvn >/dev/null 2>&1 || installer maven

if command -v mvn >/dev/null 2>&1; then
  if MVN_VERSION=$(mvn -v 2>/dev/null); then
    ok "Maven $(printf '%s\n' "$MVN_VERSION" | head -1 | awk '{print $3}')"
  else
    ko "Maven présent mais inutilisable : vérifier JAVA_HOME"
  fi
else
  ko "Maven absent (mvn) : requis pour le backend NeoFlow hors wrapper"
fi

node_ok || installer node

if node_ok; then
  ok "Node $(version_node)"
elif command -v node >/dev/null 2>&1; then
  ko "Node $(version_node) : 20+ requis"
else
  ko "Node absent : 20+ requis"
fi

if command -v npm >/dev/null 2>&1; then
  if NPM_VERSION=$(npm -v 2>/dev/null); then
    ok "npm $NPM_VERSION"
  else
    ko "npm présent mais inutilisable"
  fi
else
  ko "npm absent"
fi

python_ok || installer python

if python_ok; then
  ok "Python $(version_python) (commande : $PY)"
elif [ -n "$PY_TROUVE" ]; then
  ko "Python $PY_TROUVE : 3.11+ requis"
  info "Avec uv : uv python install 3.12"
else
  ko "Python absent : 3.11+ requis pour les laboratoires à partir du J3"
  info "Windows : vérifier les alias d'exécution python.exe/python3.exe"
fi

command -v uv >/dev/null 2>&1 || installer uv

if command -v uv >/dev/null 2>&1; then
  ok "uv $(uv --version 2>/dev/null | awk '{print $2}')"

  # Interdit à uv de télécharger Python pendant ce contrôle.
  if UV_PYTHON_DOWNLOADS=never uv python find '>=3.11' >/dev/null 2>&1; then
    ok "uv trouve un interpréteur Python 3.11+"
  else
    warn "uv ne trouve pas de Python 3.11+ : uv python install 3.12"
  fi
else
  ko "uv absent"
  info "Windows : winget install astral-sh.uv ; macOS : brew install uv"
  info "Linux : curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

if [ "$WINGET_FAIT" -eq 1 ]; then
  warn "Outils installés par winget : fermer et rouvrir Git Bash, puis relancer le script"
fi

if command -v docker >/dev/null 2>&1; then
  ok "Docker présent (PostgreSQL, Jaeger, Qdrant, Ollama)"
else
  warn "Docker absent : non bloquant en J1, requis pour certains laboratoires"
fi

# ---------------------------------------------------------------------------
# 2. OpenCode — version 2.x obligatoire
# ---------------------------------------------------------------------------

titre "2. OpenCode — version 2.x requise"

OPENCODE_V2=0

instructions_opencode_v2() {
  info "Documentation : https://opencode.ai/docs/"
  info "Migration V1 : https://opencode.ai/docs/migrate-v1/"

  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
      info "Windows : télécharger le binaire CLI autonome depuis la documentation"
      info "Placer opencode.exe dans un dossier du PATH, puis rouvrir Git Bash"
      ;;
    *)
      info "Installation V2 : curl -fsSL https://opencode.ai/v2/install | bash"
      info "Avec npm, retirer d'abord une ancienne installation npm V1 :"
      info "npm uninstall -g opencode-ai"
      info "npm install -g @opencode/cli"
      ;;
  esac

  info "Vérification : opencode --version"
}

if command -v opencode >/dev/null 2>&1; then
  if SORTIE_VERSION=$(opencode --version 2>/dev/null); then
    OV=$(printf '%s\n' "$SORTIE_VERSION" |
      grep -oE '[0-9]+\.[0-9]+\.[0-9]+' |
      head -1)

    case "$OV" in
      2.*)
        OPENCODE_V2=1
        ok "OpenCode $OV"
        ;;
      "")
        ko "OpenCode présent, mais version impossible à déterminer"
        instructions_opencode_v2
        ;;
      *)
        ko "OpenCode $OV : version 2.x obligatoire"
        instructions_opencode_v2
        ;;
    esac
  else
    ko "La commande opencode --version échoue"
    instructions_opencode_v2
  fi
else
  ko "OpenCode absent : version 2.x obligatoire"
  instructions_opencode_v2
fi

# ---------------------------------------------------------------------------
# 3. Accès aux modèles Anthropic
# ---------------------------------------------------------------------------

titre "3. Accès aux modèles (clé API Anthropic)"

AUTH_FILE="${XDG_DATA_HOME:-$HOME/.local/share}/opencode/auth.json"

if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  case "$ANTHROPIC_API_KEY" in
    sk-ant-*)
      ok "ANTHROPIC_API_KEY définie (préfixe sk-ant-, ${#ANTHROPIC_API_KEY} caractères)"
      ;;
    *)
      warn "ANTHROPIC_API_KEY définie mais préfixe inattendu"
      ;;
  esac
elif [ -f "$AUTH_FILE" ] &&
     grep -q '"anthropic"' "$AUTH_FILE" 2>/dev/null; then
  ok "Entrée Anthropic trouvée dans $AUTH_FILE"
  info "Présence détectée uniquement : validité du justificatif non vérifiée"
else
  ko "Aucune clé : définir ANTHROPIC_API_KEY ou connecter Anthropic dans OpenCode avec /connect"
fi

if [ "$SANS_RESEAU" -eq 0 ] &&
   [ -n "${ANTHROPIC_API_KEY:-}" ]; then

  if command -v curl >/dev/null 2>&1; then
    CODE=$(curl -s -o /dev/null -w '%{http_code}' \
      --max-time 15 \
      https://api.anthropic.com/v1/models \
      -H "x-api-key: ${ANTHROPIC_API_KEY}" \
      -H "anthropic-version: 2023-06-01")

    case "$CODE" in
      200)
        ok "API Anthropic joignable, clé acceptée (GET /v1/models)"
        ;;
      401)
        ko "Clé Anthropic refusée (401)"
        ;;
      403)
        ko "Accès Anthropic interdit (403) : vérifier les droits du compte"
        ;;
      000)
        ko "API Anthropic injoignable : proxy, pare-feu ou réseau (HTTPS_PROXY ?)"
        ;;
      *)
        warn "Réponse inattendue de l'API Anthropic : HTTP $CODE"
        ;;
    esac
  else
    warn "curl absent : test de l'API Anthropic ignoré"
  fi
fi

if [ "$SANS_RESEAU" -eq 0 ] && [ "$OPENCODE_V2" -eq 1 ]; then
  if CATALOGUE=$(opencode models 2>/dev/null); then
    MODELES=$(printf '%s\n' "$CATALOGUE" | grep '^anthropic/' || true)
    NB=$(printf '%s\n' "$MODELES" | grep -c '^anthropic/' || true)

    if [ "$NB" -eq 0 ]; then
      ko "Aucun modèle anthropic/ dans le catalogue OpenCode"
    else
      ok "$NB modèles anthropic/ dans le catalogue OpenCode"
    fi

    # Modèles de référence conservés depuis le script fourni.
    # Leur présence dans le catalogue ne garantit pas les droits du compte.
    for m in claude-sonnet-5-5 claude-opus-5-5 claude-haiku-5-5; do
      if printf '%s\n' "$MODELES" | grep -qx "anthropic/$m"; then
        ok "anthropic/$m présent au catalogue (requis)"
      else
        ko "anthropic/$m absent du catalogue (requis)"
      fi
    done

    for m in claude-opus-5-5-fast claude-fable-5-2 claude-fable-5-2-fast; do
      if printf '%s\n' "$MODELES" | grep -qx "anthropic/$m"; then
        info "anthropic/$m présent au catalogue (optionnel)"
      else
        info "anthropic/$m absent du catalogue (optionnel)"
      fi
    done

    ANCIENS=$(printf '%s\n' "$MODELES" |
      grep -cE '^anthropic/claude-(haiku|sonnet|opus)-4-' || true)

    if [ "$ANCIENS" -gt 0 ]; then
      info "$ANCIENS modèles de génération 4.x listés : non utilisés dans la formation"
    fi
  else
    ko "Échec de opencode models : vérifier le réseau et la configuration"
  fi
fi

# ---------------------------------------------------------------------------
# 4. Dépôt et configuration projet
# ---------------------------------------------------------------------------

titre "4. Dépôt courant ($(pwd))"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  ok "Dépôt Git : branche $(git branch --show-current 2>/dev/null)"

  # Recherche dans le contenu courant des fichiers suivis.
  # Aucune valeur trouvée n'est affichée.
  git grep -nI -E 'sk-ant-[A-Za-z0-9_-]{10,}' -- . >/dev/null 2>&1
  STATUT_GREP=$?

  case "$STATUT_GREP" in
    0)
      ko "Une clé Anthropic semble présente dans les fichiers suivis"
      ;;
    1)
      ok "Aucune clé Anthropic détectée dans le contenu courant des fichiers suivis"
      ;;
    *)
      warn "Recherche des clés impossible dans les fichiers suivis"
      ;;
  esac

  if [ -x backend/mvnw ]; then
    ok "backend/mvnw exécutable"
  else
    warn "backend/mvnw introuvable ou non exécutable"
    info "Lancer depuis la racine NeoFlow ; si nécessaire : chmod +x backend/mvnw"
  fi
else
  warn "Pas dans un dépôt Git : vérifications Git ignorées"
fi

CONFIG_PRESENTE=0

for f in \
  opencode.json \
  opencode.jsonc \
  .opencode/opencode.json \
  .opencode/opencode.jsonc; do
  if [ -f "$f" ]; then
    CONFIG_PRESENTE=1
    break
  fi
done

if [ "$CONFIG_PRESENTE" -eq 1 ]; then
  if [ "$OPENCODE_V2" -ne 1 ]; then
    warn "Configuration projet non vérifiée : OpenCode 2.x requis"
  elif [ -z "$PY" ]; then
    ko "Configuration projet non vérifiée : Python 3.11+ requis"
  else
    # Ne jamais afficher la configuration complète :
    # elle peut contenir des informations sensibles.
    if CFG=$(opencode debug config 2>/dev/null); then
      printf '%s' "$CFG" | run_py -c '
import json
import sys

try:
    c = json.load(sys.stdin)
except (ValueError, TypeError):
    print("  \033[31mKO\033[0m    Configuration non exploitable : JSON attendu")
    sys.exit(1)

if not isinstance(c, dict):
    print("  \033[31mKO\033[0m    Configuration non exploitable : objet JSON attendu")
    sys.exit(1)

n = 0

def p(condition, message):
    global n
    if condition:
        prefix = "  \033[32mOK\033[0m    "
    else:
        prefix = "  \033[31mKO\033[0m    "
        n += 1
    print(prefix + message)

# V2 utilise update ; V1 utilisait autoupdate.
if "update" in c:
    updates_disabled = c.get("update") == "disable"
else:
    updates_disabled = c.get("autoupdate") is False

p(updates_disabled, "Mises à jour automatiques désactivées")

model = c.get("model")
p(
    isinstance(model, str) and model.startswith("anthropic/"),
    "Modèle principal Anthropic configuré"
)

# Ces contrôles vérifient la présence des règles attendues.
# Ils ne simulent pas le moteur complet de permissions OpenCode,
# ni les permissions propres aux agents ou les politiques système.

if isinstance(c.get("permissions"), list):
    rules = c["permissions"]

    def explicit_deny(action, resources):
        return any(
            isinstance(rule, dict)
            and rule.get("action") == action
            and rule.get("resource") in resources
            and rule.get("effect") == "deny"
            for rule in rules
        )

    p(
        explicit_deny("read", {"*.env", "*"}),
        "Règle deny de lecture de *.env présente"
    )
    p(
        explicit_deny("shell", {"git push*", "*"}),
        "Règle deny de git push présente"
    )
    p(
        explicit_deny("webfetch", {"*"}),
        "Règle deny de webfetch présente"
    )

else:
    perm = c.get("permission")
    if not isinstance(perm, dict):
        perm = {}

    def legacy_deny(action, pattern):
        value = perm.get(action)
        if value == "deny":
            return True
        return (
            isinstance(value, dict)
            and (
                value.get(pattern) == "deny"
                or value.get("*") == "deny"
            )
        )

    p(
        legacy_deny("read", "*.env"),
        "Règle deny de lecture de *.env présente (format V1)"
    )
    p(
        legacy_deny("bash", "git push*"),
        "Règle deny de git push présente (format V1)"
    )
    p(
        legacy_deny("webfetch", "*"),
        "Règle deny de webfetch présente (format V1)"
    )

print(
    "  \033[36mINFO\033[0m  Contrôle de présence des règles ; "
    "les exceptions et permissions propres aux agents restent à examiner"
)

# share était contrôlé dans le script V1.
# Il ne constitue plus ici un critère bloquant.
if "share" in c:
    print(
        "  \033[36mINFO\033[0m  Champ share hérité présent : "
        "son comportement dépend de la version OpenCode"
    )

sys.exit(min(n, 100))
'
      STATUT_CONFIG=$?
      KO=$((KO + STATUT_CONFIG))
    else
      ko "Impossible de lire la configuration avec opencode debug config"
      info "Vérifier la configuration et les commandes disponibles dans cette version"
    fi
  fi
else
  warn "Pas de configuration OpenCode dans le projet : contrôle ignoré"
fi

# ---------------------------------------------------------------------------
# Bilan
# ---------------------------------------------------------------------------

titre "Bilan"

printf '  %s bloquant(s), %s avertissement(s)\n' "$KO" "$WARN"

[ "$KO" -eq 0 ]