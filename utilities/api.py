from typing import Union, Annotated, Optional
from fastapi import FastAPI, File, UploadFile, Path, Form, Query
from pydantic import BaseModel
import singleton
import hashlib
import time
import sys
import json
if sys.version_info < (3, 6):
    import sha3


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

        @self.app.get("/api/getProducers/{text}")
        async def check_producer(text: Annotated[str, Path(title="The ID of the item to get")]):
            return self.s.Query.get_producers(filter_value=text)

        @self.app.post("/api/dlSim/")
        async def get_sim(
                st1: str = Form(...),
                st2: str = Form(...),
        ):
            return self.s.Similarity.dl_sim(st1,st2)

        @self.app.post("/api/getCountries/")
        async def create_get_countries(
                producer: str = Form(...),
                cuvees: str = Form(...),
                vintage: int | str = Form(...),
        ):

            producer_dict = json.loads(producer)
            cuvees_dict = json.loads(cuvees)

            return self.s.Query.assemble_wine_data(producer=producer_dict, filter_cuvee=cuvees_dict, vintage=vintage)

        @self.app.post("/api/addWine")
        async def add_wine(producer: Annotated[str, Form()], cuvee: Annotated[str, Form()], vintage: Annotated[str, Form()]):
            return {"success": True}

        @self.app.post("/api/uploadfile/{user_id}")
        async def create_upload_file(
                user_id: Annotated[str, Path(title="The ID of the item to get")],
                file: UploadFile | None = None,
                q: str | None = None,
                item: Item | None = None,
        ):
            # Write to file
            contents = await file.read()

            # initiating the "s" object to use the
            # sha3_224 algorithm from the hashlib module.
            s = hashlib.sha3_224()
            string = (user_id + str(time.time())).encode()
            # providing the input to the hashing algorithm.
            s.update(string)

            filename = (s.hexdigest())

            results = {"user_id": user_id}
            if q:
                results.update({"q": q})
            if item:
                results.update({"item": item})
            path = 'tmp/' + filename + '.pdf'
            self.s.Save.owner_id = user_id
            self.s.Save.path = path
            if file:
                with open('tmp/' + filename + '.pdf', 'wb') as f:
                    f.write(contents)
                    results.update({"filename" : file.filename})
                    self.s.Save.filename = file.filename
            self.s.Save.reset()
            self.s.Parser.reset()
            self.s.Parser.load(path)
            results.update(self.s.Save.response)
            return results
