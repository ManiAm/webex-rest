
import sys
import logging
from dotenv import load_dotenv
from webex_api import WEBEX_API

logging.basicConfig(level=logging.INFO, format='%(message)s')

log = logging.getLogger(__name__)

load_dotenv()


if __name__ == "__main__":

    webex = WEBEX_API()

    team_name = "Project Alpha"
    room_titles = ["Dev Room", "QA Room"]

    # Map room title to list of user emails
    room_user_map = {
        "Dev Room": ["alice@example.com", "bob@example.com", "charlie@example.com"],
        "QA Room": ["diana@example.com", "eve@example.com"]
    }

    #############################
    # Step 1: Get or create team
    #############################

    status, teams = webex.get_teams(team_name=team_name)
    if not status:
        log.error("Failed to get teams: %s", teams)
        sys.exit(1)

    if teams:
        team_id = teams[0]["id"]
        log.info("Team '%s' already exists. Skipping creation.", team_name)
    else:
        status, team = webex.create_team(team_name)
        if not status:
            log.error("Team creation failed: %s", team)
            sys.exit(1)
        team_id = team["id"]
        log.info("Created team: %s", team["name"])

    ###########################################
    # Step 2: Get or create rooms under team
    ###########################################

    room_ids = {}

    for title in room_titles:

        status, rooms = webex.get_rooms(team_id=team_id, room_title=title)
        if not status:
            log.error("Failed to get rooms: %s", rooms)
            sys.exit(1)

        if rooms:
            room_id = rooms[0]["id"]
            log.info("Room '%s' already exists. Skipping creation.", title)
        else:
            status, room = webex.create_room(room_title=title, team_id=team_id)
            if not status:
                log.error("Room creation failed: %s", room)
                sys.exit(1)
            room_id = room["id"]
            log.info("Created room: %s", title)

        room_ids[title] = room_id

    #################################
    # Step 3: Add users to the team
    #################################

    all_users = set(email for user_list in room_user_map.values() for email in user_list)

    for email in all_users:

        status, added = webex.add_team_member(team_id=team_id, person_id=None, person_email=email, is_moderator=False)
        if not status and "409" not in str(added):
            log.error("Adding team member %s failed: %s", email, added)
            continue

        log.info("Added %s to team (or already exists)", email)

    #######################################
    # Step 4: Add same users to each room
    #######################################

    for room_title, user_list in room_user_map.items():

        room_id = room_ids[room_title]

        for email in user_list:

            status, added = webex.add_room_member(room_id=room_id, person_id=None, person_email=email, is_moderator=False)
            if not status and "409" not in str(added):
                log.error("Adding %s to room %s failed: %s", email, room_title, added)
                continue

            log.info("Added %s to room %s (or already exists)", email, room_title)

    ############################################
    # Step 5: Post welcome message in each room
    ############################################

    for room_title, room_id in room_ids.items():

        welcome_message = f"👋 Welcome to the *{room_title}*!"
        status, response = webex.create_message(room_id=room_id, text=welcome_message)
        if not status:
            log.error("Failed to send welcome message to room %s: %s", room_title, response)
        else:
            log.info("Sent welcome message to room: %s", room_title)
