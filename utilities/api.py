from mimetypes import inited
from typing import Union, Annotated, Optional
from fastapi import FastAPI, File, UploadFile, Path, Form, Query
from lxml.html.builder import FRAME
from lxml.xslt import exception
from matplotlib.font_manager import json_load
from pydantic import BaseModel
import singleton
import hashlib
import time
import sys
import json
from utilities.queryDB import Query
from utilities.save import Save
from utilities.parser import Parser
from utilities.recommender import Recommender
from utilities.user import User
from utilities.handle_user_wine import HandleUserWine
from custom_types.Flight import Flight
from custom_types.UserType import UserType
from pathlib import Path as PathlibPath  # Avoid conflict with FastAPI's Path

class Item(BaseModel):
    name: str


class API:

    def __init__(self):
        # Initialize the FastAPI app as an instance variable
        self.app = FastAPI()
        self.setup_routes()
        self.s = singleton.Singleton()

    def setup_routes(self):
        # Define a function within the setup_routes method
        # And then use the decorator from the instance variable app

        @self.app.get("/api/")
        def read_root():
            return {self.s.hello()}

        @self.app.get("/api/items/{user_id}")
        def read_item(user_id: int, q: Union[str, None] = None):
            return {"user_id": user_id, "q": q}

        @self.app.post("/api/files/")
        async def create_file(file: Annotated[bytes, File()]):
            return {"file_size": len(file)}

        @self.app.post("/api/getProducers/")
        async def check_producer(
                text: str = Form(...),
        ):
            query = Query()
            return query.get_producers(filter_value=text, with_keys=True)

        @self.app.post("/api/recs/")
        async def get_recs(
                slug: str = Form(...),
                text: str = Form(...),
                deps: str | None = Form(None),
        ):
            recommender = Recommender()
            data = recommender.get_recommendation(class_name=slug, text=text, deps=deps)
            json_data = json.dumps(data)
            return json_data

        @self.app.post("/api/updateUser/")
        async def update_user(
                data: str = Form(...),
        ):
            user = User()
            response = user.update_user(data=data)
            return True if response.update_time else False

        @self.app.post("/api/searchUser/")
        async def update_user(
                data: str = Form(...),
        ):
            user = User()
            return user.search_for_user(data=data)

        @self.app.post("/api/groupShare/")
        async def update_user(
                data: str = Form(...),
                groupId: str = Form(...),
                ownerId: str = Form(...),
                key: str = Form(...),
        ):
            return self.s.Shares.handle_group_share(data=data, group_id=groupId, owner_id=ownerId, key=key)

        @self.app.post("/api/groupRequest/")
        async def update_user(
                data: str = Form(...),
                owner: str = Form(...),
        ):
            return self.s.Group.create_group(data=data, owner=owner)

        @self.app.post("/api/createWine/")
        async def update_user(
                owner: str = Form(...),
                wineData: str = Form(...),
                flightData: str = Form(...),
        ):
            handle_user_wine = HandleUserWine()
            return handle_user_wine.handle_upload(wine=wineData, flight=flightData, owner=owner.replace('"', ''))

        @self.app.post("/api/messageMeta/")
        async def message_meta(
                groupId: str=Form(...),
                message: str=Form(...),
        ):
            message_object = json.loads(message)
            message_object['timestamp'] = self.s.Messages.generate_timestamp()
            data = {'last_message': message_object}
            group_str = groupId.replace('"', '')
            success = self.s.Cacher.set_data('group:' + group_str, data, '', False)
            return success

        @self.app.post("/api/getRecentGroupInfo")
        async def get_recent_group_info(
                groupId: str=Form(...),
        ):
            group_str = groupId.replace('"', '')
            data = self.s.Cacher.get_data('group:' + group_str)
            if data is not None and data[0] and len(data) > 0:
                try:
                    uid = data[0]['last_message']['owner']
                except exception as e:
                    return False
                user = UserType(decoded_data=self.s.Cacher.get_data('users:' + uid)[0], key=uid)
                initials = user.get_initials()
                return {'user': initials, 'data': data[0]}
            return False

        @self.app.post("/api/getUsername/")
        async def get_user_names(
                uids: str = Form(...),
        ):
            uids_list = json.loads(uids)
            names_list = []
            for uid in uids_list:
                user = UserType(decoded_data=self.s.Cacher.get_data('users:' + uid)[0], key=uid)
                names_list.append(user.get_user_name())
            return json.dumps(names_list)

        @self.app.post("/api/createFlight/")
        async def update_user(
                owner: str = Form(...),
                name: str = Form(...),
        ):
            flight = Flight()
            flight.owner_id = json.loads(owner)
            flight.title = json.loads(name)
            flight.current_version = 1
            flight.versions = {'1': []}
            if flight.title and len(flight.title) > 0:
                return {'id': flight.create_flight()}
            else:
                return "Can't create a nameless flight"

        @self.app.post("/api/dlSim/")
        async def get_sim(
                st1: str = Form(...),
                st2: str = Form(...),
        ):
            return self.s.Similarity.dl_sim(st1, st2)

        @self.app.post("/api/getCountries/")
        async def create_get_countries(
                producer: str = Form(...),
                cuvee: str = Form(...),
                vintage: str = Form(...),
        ):
            producer_dict = json.loads(producer)
            cuvee_dict = json.loads(cuvee)
            vintage_dict = json.loads(vintage)
            return self.s.Save.assemble_wine_data(producer=producer_dict, filter_cuvee=cuvee_dict,
                                                  vintage=vintage_dict)

        @self.app.post("/api/addWine")
        async def add_wine(producer: Annotated[str, Form()], cuvee: Annotated[str, Form()],
                           vintage: Annotated[str, Form()]):
            return {"success": True}

        @self.app.post("/api/uploadfile/{user_id}")
        async def create_upload_file(
                user_id: Annotated[str, Path(title="The ID of the item to get")],  # FastAPI's Path
                file: UploadFile | None = None,
                q: str | None = None,
                item: Item | None = None,
        ):
            # Write to file
            contents = await file.read()

            # Initiating the "s" object to use the sha3_224 algorithm from the hashlib module.
            s = hashlib.sha3_224()
            string = (user_id + str(time.time())).encode()
            # Providing the input to the hashing algorithm.
            s.update(string)

            filename = (s.hexdigest())
            self.s.Save.reset()
            results = {"user_id": user_id}
            if q:
                results.update({"q": q})
            if item:
                results.update({"item": item})

            # Use PathlibPath to create the directory and file path
            tmp_dir = PathlibPath("tmp")
            tmp_dir.mkdir(parents=True, exist_ok=True)  # Ensure 'tmp' directory exists

            # Build the file path in a cross-platform way
            path = tmp_dir / f"{filename}.pdf"
            self.s.Save.owner_id = user_id
            self.s.Save.path = str(path)  # Convert Path object to string if needed

            if file:
                # Write the file
                with open(path, 'wb') as f:
                    f.write(contents)
                    results.update({"filename": file.filename})
                    self.s.Save.filename = file.filename

            self.s.P3.reset()
            self.s.P3.load(str(path), user_id, file.filename)  # Ensure path is a string for P3.load
            self.s.P3.close_out()
            results.update(self.s.Save.response)
            return results
