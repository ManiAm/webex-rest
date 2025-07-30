
import sys
import os
import getpass
import json
import logging
import requests

log = logging.getLogger(__name__)


class WEBEX_API():

    def __init__(self,
                 url=None,
                 api_version='v1',
                 user=getpass.getuser()):

        if not url:
            url = "https://webexapis.com"

        self.baseurl = f'{url}/{api_version}'

        access_token = os.getenv('WEBEX_API_TOKEN', None)
        if not access_token:
            log.error("cannot read 'WEBEX_API_TOKEN' env variable")
            sys.exit(2)

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        self.user = user


    #####################
    ####### rooms #######
    #####################

    # Rooms are virtual meeting places where people post
    # messages and collaborate to get work done.

    def get_rooms(self, team_id=None, room_type=None, max_items=100, room_title=None):
        """
            room_type: direct, group
        """

        url = f"{self.baseurl}/rooms"

        params = {
            "teamId": team_id,
            "type": room_type,
            "max": max_items
        }

        status, output = self.__request("GET", url, params=params)
        if not status:
            return False, output

        items = output.get("items", [])

        if room_title:
            for item in items[:]:
                title = item.get("title", None)
                if not title or title != room_title:
                    items.remove(item)

        return True, items


    def get_room_details(self, room_id):

        url = f"{self.baseurl}/rooms/{room_id}"

        status, output = self.__request("GET", url)
        if not status:
            return False, output

        return True, output


    def create_room(self,
                    room_title,
                    team_id=None,
                    description=None,
                    isLocked=False,
                    isPublic=False,
                    isAnnouncementOnly=False):

        url = f"{self.baseurl}/rooms"

        params = {
            "title": room_title,
            "teamId": team_id,
            "description": description,
            "isLocked": isLocked,
            "isPublic": isPublic,
            "isAnnouncementOnly": isAnnouncementOnly
        }

        status, output = self.__request("POST", url, json=params)
        if not status:
            return False, output

        return True, output


    def delete_room_by_id(self, room_id):

        url = f"{self.baseurl}/rooms/{room_id}"

        status, output = self.__request("DELETE", url)
        if not status:
            return False, output

        return True, output


    def delete_room_by_title(self, room_title):

        status, output = self.get_rooms(room_title=room_title)
        if not status:
            return False, output

        if not output:
            return False, f"cannot find any rooms with title '{room_title}'"

        if len(output) > 1:
            log.warning("more than one rooms found with title '%s'. Deleting the first one.", room_title)

        first_room = output[0]

        room_id = first_room.get("id", None)
        if not room_id:
            return False, f"cannot get the room_id of {room_title}"

        return self.delete_room_by_id(room_id)


    ###############################
    ####### room membership #######
    ###############################

    # Memberships represent a person's relationship to a room.

    def get_room_members(self, room_id):
        """
            NOTE: direct rooms have two members
        """

        url = f"{self.baseurl}/memberships"

        params = {
            "roomId": room_id
        }

        status, output = self.__request("GET", url, params=params)
        if not status:
            return False, output

        items = output.get("items", [])

        return True, items


    def add_room_member(self, room_id, person_id, person_email, is_moderator):

        url = f"{self.baseurl}/memberships"

        params = {
            "roomId": room_id,
            "personId": person_id,
            "personEmail": person_email,
            "isModerator": is_moderator
        }

        status, output = self.__request("POST", url, json=params)
        if not status:
            return False, output

        return True, output


    def delete_room_member(self, membership_id):

        url = f"{self.baseurl}/memberships/{membership_id}"

        status, output = self.__request("DELETE", url)
        if not status:
            return False, output

        return True, output


    #####################
    ####### teams #######
    #####################

    # Teams are groups of people with a set of rooms
    # that are visible to all members of that team.

    def get_teams(self, team_name=None, max_items=100):

        url = f"{self.baseurl}/teams"

        params = {
            "max": max_items
        }

        status, output = self.__request("GET", url, params=params)
        if not status:
            return False, output

        items = output.get("items", [])

        if team_name:
            for item in items[:]:
                name = item.get("name", None)
                if not name or name != team_name:
                    items.remove(item)

        return True, items


    def create_team(self, name):

        url = f"{self.baseurl}/teams"

        params = {
            "name": name
        }

        status, output = self.__request("POST", url, json=params)
        if not status:
            return False, output

        return status, output


    ###############################
    ####### team membership #######
    ###############################

    def get_team_members(self, team_id):

        url = f"{self.baseurl}/team/memberships"

        params = {
            "teamId": team_id
        }

        status, output = self.__request("GET", url, params=params)
        if not status:
            return False, output

        items = output.get("items", [])

        return True, items


    def add_team_member(self, team_id, person_id, person_email, is_moderator):

        url = f"{self.baseurl}/team/memberships"

        params = {
            "teamId": team_id,
            "personId": person_id,
            "personEmail": person_email,
            "isModerator": is_moderator
        }

        status, output = self.__request("POST", url, json=params)
        if not status:
            return False, output

        return True, output


    def delete_team_member(self, membership_id):

        url = f"{self.baseurl}/team/memberships/{membership_id}"

        status, output = self.__request("DELETE", url)
        if not status:
            return False, output

        return True, output


    ######################
    ####### groups #######
    ######################

    # Groups contain a collection of members in Webex.
    # A member represents a Webex user. A group is used to assign
    # templates and settings to the set of members contained in a group.

    def get_groups(self, count=100):

        url = f"{self.baseurl}/groups"

        params = {
            "count": count
        }

        status, output = self.__request("GET", url, params=params)
        if not status:
            return False, output

        items = output.get("items", [])

        return True, items


    ######################
    ####### people #######
    ######################

    # People are registered users of Webex.

    def get_people(self,
                   email=None,
                   display_name=None,
                   people_id=None,
                   org_id=None,
                   roles=None,
                   location_id=None,
                   max_items=100):
        """
            email, display_name, role, or id should be specified
        """

        url = f"{self.baseurl}/people"

        params = {
            "email": email,
            "displayName": display_name,
            "id": people_id,
            "orgId": org_id,
            "roles": roles,
            "locationId": location_id,
            "max": max_items
        }

        status, output = self.__request("GET", url, params=params)
        if not status:
            return False, output

        items = output.get("items", [])

        return True, items


    def get_myself(self):

        url = f"{self.baseurl}/people/me"

        status, output = self.__request("GET", url)
        if not status:
            return False, output

        return True, output


    ############################
    ####### organization #######
    ############################

    # A set of people in Webex.
    # Organizations may manage other organizations or be managed themselves.

    def get_organization(self, display_name=None, org_id=None):

        url = f"{self.baseurl}/organizations"

        params = {
            "displayName": display_name,
            "id": org_id
        }

        status, output = self.__request("GET", url, params=params)
        if not status:
            return False, output

        items = output.get("items", [])

        return True, items


    ########################
    ####### meetings #######
    ########################

    # Meetings are virtual conferences where users can collaborate in
    # real time using audio, video, content sharing, chat,
    # online whiteboards, and to collaborate.

    def get_meetings(self,
                     meetingNumber=None,
                     web_link=None,
                     room_id=None,
                     meeting_type=None,
                     meeting_state=None,
                     max_items=10):

        url = f"{self.baseurl}/meetings"

        params = {
            "meetingNumber": meetingNumber,
            "webLink": web_link,
            "roomId": room_id,
            "meetingType": meeting_type,
            "state": meeting_state,
            "max": max_items
        }

        status, output = self.__request("GET", url, params=params)
        if not status:
            return False, output

        items = output.get("items", [])

        return True, items


    ##########################
    ####### recordings #######
    ##########################

    # Recordings are meeting content captured in a meeting or
    # files uploaded via the upload page for your Webex site.

    def get_recordings(self,
                       meeting_id=None,
                       max_items=10):

        url = f"{self.baseurl}/recordings"

        params = {
            "meetingId": meeting_id,
            "max": max_items
        }

        status, output = self.__request("GET", url, params=params)
        if not status:
            return False, output

        items = output.get("items", [])

        return True, items


    ########################
    ####### messages #######
    ########################

    # Messages are how you communicate in a room. In Webex, each message is
    # displayed on its own line along with a timestamp and sender information.

    def get_messages(self, room_id, parent_id=None, max_items=50):

        url = f"{self.baseurl}/messages"

        params = {
            "roomId": room_id,
            "parentId": parent_id,
            "max": max_items
        }

        status, output = self.__request("GET", url, params=params)
        if not status:
            return False, output

        items = output.get("items", [])

        return True, items


    def get_direct_messages(self, parent_id=None, person_id=None, person_email=None):

        url = f"{self.baseurl}/messages/direct"

        params = {
            "parentId": parent_id,
            "personId": person_id,
            "personEmail": person_email
        }

        status, output = self.__request("GET", url, params=params)
        if not status:
            return False, output

        items = output.get("items", [])

        return True, items


    def create_message(self,
                       room_id=None,
                       parent_id=None,
                       toPerson_id=None,
                       toPerson_email=None,
                       text=None,
                       markdown=None,
                       files=None,
                       attachments=None):
        """
            Post a 'plain text' or 'rich text' message, and
            optionally, a file attachment, to a room.
            check here: https://developer.webex.com/docs/basics#formatting-messages

            You can use 'room_id' or 'toPerson_email' for direct message
        """

        url = f"{self.baseurl}/messages"

        params = {
            "roomId": room_id,
            "parentId": parent_id,
            "toPersonId": toPerson_id,
            "toPersonEmail": toPerson_email,
            "text": text,
            "markdown": markdown,
            "files": files,
            "attachments": attachments
        }

        status, output = self.__request("POST", url, json=params)
        if not status:
            return False, output

        return True, output


    ##############################
    ####### Helper Methods #######
    ##############################

    def __request(self, method, url, **kwargs):

        try:
            response = requests.request(method,
                                        url,
                                        headers=self.headers,
                                        timeout=10,
                                        **kwargs)
        except Exception as E:
            return False, str(E)

        try:
            response.raise_for_status()
        except Exception as E:
            return False, f'Return code={response.status_code}, {E}\n{response.text}'

        try:
            content_decoded = response.content.decode('utf-8')
            if not content_decoded:
                return True, {}
            data_dict = json.loads(content_decoded)
        except Exception as E:
            return False, f'Error while decoding content: {E}'

        return True, data_dict
