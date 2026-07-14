from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / ".github" / "skills" / "pekat-vision"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
