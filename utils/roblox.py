import aiohttp
from datetime import datetime, timezone


async def fetch_roblox_user(username: str) -> dict | None:
    """
    Busca informações de um usuário Roblox pelo nickname.
    Retorna um dict com dados ou None se não encontrado.
    """
    async with aiohttp.ClientSession() as session:
        # 1) Resolver username → ID
        search_url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": False}

        async with session.post(search_url, json=payload) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            users = data.get("data", [])
            if not users:
                return None
            user_id = users[0]["id"]

        # 2) Buscar detalhes do perfil
        profile_url = f"https://users.roblox.com/v1/users/{user_id}"
        async with session.get(profile_url) as resp:
            if resp.status != 200:
                return None
            profile = await resp.json()

        # 3) Buscar avatar headshot
        avatar_url = (
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot"
            f"?userIds={user_id}&size=420x420&format=Png&isCircular=false"
        )
        avatar_thumb = None
        async with session.get(avatar_url) as resp:
            if resp.status == 200:
                thumb_data = await resp.json()
                thumbs = thumb_data.get("data", [])
                if thumbs:
                    avatar_thumb = thumbs[0].get("imageUrl")

    # Formatar data de criação
    created_raw = profile.get("created", "")
    try:
        created_dt = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
        created_str = created_dt.strftime("%d/%m/%Y")
    except Exception:
        created_str = created_raw

    return {
        "id": user_id,
        "username": profile.get("name", username),
        "display_name": profile.get("displayName", username),
        "description": profile.get("description", ""),
        "created": created_str,
        "avatar_url": avatar_thumb,
        "profile_link": f"https://www.roblox.com/users/{user_id}/profile",
    }
