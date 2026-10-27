# Agent Reach en español (fork)

Fork personal de [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) con la interfaz en español.

## Qué cambia respecto al original

- **Skill en español** (`agent_reach/skill/SKILL_es.md` y `references/sesiones.md`, `capacidades.md`, `mantenimiento.md`). Es la que se instala por defecto; `AGENT_REACH_LANG=en` o `AGENT_REACH_LANG=zh` instalan la inglesa o la china.
- **Informe de instalación, estados y mensajes de error** en español.
- **Navegador propio en español** (`es-ES`), así las páginas de inicio de sesión ya no salen en chino.
- **Subtítulos de YouTube** en español primero y luego en inglés (antes, chino). Se puede pedir otro idioma con `--lang`.

Las palabras chinas que el código usa para detectar errores de webs chinas (Bilibili, Xiaohongshu, Boss Zhipin…) se mantienen a propósito: son funcionales.

## Instalar desde este fork

Se instala en modo editable, apuntando a la carpeta del repositorio. Así los cambios del código se aplican al momento y `agent-reach update` no lo sustituye por la versión original:

```bash
uv tool install --force --editable C:\Users\Jonni\Documents\Personal-Workspace\Agent-Reach
agent-reach setup
```

`agent-reach update` sigue actualizando las herramientas de cada canal y la skill.

## Traer cambios del proyecto original

Es automático, en dos pasos:

1. **GitHub → fork** ([sync-upstream.yml](../.github/workflows/sync-upstream.yml)): cada lunes fusiona el `main` del original en el `main` del fork. Si la fusión es limpia y los tests pasan, la sube sola. Si hay conflictos, fallan los tests o el original cambió un workflow, abre un issue con lo que hay que hacer y no toca `main`. También se puede lanzar a mano desde la pestaña Actions.
2. **Fork → esta carpeta** ([sync-local.ps1](../scripts/sync-local.ps1)): cada día trae el `main` del fork a la carpeta local, solo si está en `main`, sin cambios a medias y sin commits pendientes de subir. Si cambian las dependencias, reinstala Agent Reach. Deja un registro en `~/.agent-reach/fork-sync.log`. Se registra una vez con:

   ```bash
   powershell -ExecutionPolicy Bypass -File scripts\sync-local.ps1 -Register
   ```

A mano, si hay conflictos:

```bash
git pull upstream main
git push origin main
```

Los conflictos suelen estar en los textos traducidos: conserva el texto en español y aplica el cambio de lógica del original.
