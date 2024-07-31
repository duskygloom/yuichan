from utils.secret import *

integration_t = {
    "guild_install": 0,
    "user_install": 1
}


def main():
    secret = load_secret()
    url = "https://discord.com/oauth2/authorize?"
    url += f"client_id={secret['application_id']}&"
    url += f"permissions={secret['permissions']}&"
    url += f"integration_type={integration_t['guild_install']}&"
    url += f"scope={'+'.join(secret['scopes'])}"
    print(url)


if __name__ == "__main__":
    main()
