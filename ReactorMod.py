"""
  __  ___  _____  ____________  ______ ___ 
 / / / / |/ / _ \/ __/ __<  / |/ /_  // _ \
/ /_/ /    / // / _// _/ / /    //_ </ // /
\____/_/|_/____/___/_/  /_/_/|_/____/____/

©️ 2025 — licensed under Apache 2.0 

🌐 https://www.apache.org/licenses/LICENSE-2.0

"""

#meta developer: @undef1n3dd

import asyncio

from .. import loader, utils

from legacytl.types import Message
from legacytl.tl.types import MessageEntityCustomEmoji

@loader.tds
class ReactorMod(loader.Module):
    strings = {
        "name": "Reactor",
        "_cfg_silent": "React silently",
        "incorrect_format": "<emoji document_id=5881702736843511327>⚠️</emoji> <b>Incorrect format</b>",
        "reaction_added": "<emoji document_id=5776375003280838798>✅</emoji><b> Reaction</b> <code>{}</code> <b>with emoji</b> <code>{}</code> <b>successfully added</b>",
        "reaction_removed": "<emoji document_id=5879896690210639947>🗑</emoji> <b>Reaction</b> <code>{}</code> <b>removed</b>",
        "not_found": "<emoji document_id=6037243349675544634>👁</emoji> <b>Reaction</b> <code>{}</code> <b>not found</b>",
        "no_reply": "<emoji document_id=5879813604068298387>❗️</emoji> <b>Reply to message</b>",
        "reactions_list": "<emoji document_id=5766994197705921104>🗂</emoji> <b>List of available reactions:</b>\n\n{}",
        "done": "<emoji document_id=5776375003280838798>✅</emoji> <b>Done</b>"
    }

    strings_ru = {
        "_cfg_silent": "Молча отреагировать",
        "incorrect_format": "<emoji document_id=5881702736843511327>⚠️</emoji> <b>Неправильный формат</b>",
        "reaction_added": "<emoji document_id=5776375003280838798>✅</emoji><b> Реакция</b> <code>{}</code> <b>с эмоджи</b> <code>{}</code> <b>успешно добавлена</b>",
        "reaction_removed": "<emoji document_id=5879896690210639947>🗑</emoji> <b>Реакция</b> <code>{}</code> <b>удалена</b>",
        "not_found": "<emoji document_id=6037243349675544634>👁</emoji> <b>Реакция</b> <code>{}</code> <b>не найдена</b>",
        "no_reply": "<emoji document_id=5879813604068298387>❗️</emoji> <b>Ответьте на сообщение</b>",
        "reactions_list": "<emoji document_id=5766994197705921104>🗂</emoji> <b>Список доступных реакций:</b>\n\n{}",
        "done": "<emoji document_id=5776375003280838798>✅</emoji> <b>Готово</b>"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "silent",
                False,
                lambda: self.strings("_cfg_silent"),
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, _):
        self._client = client
        self.reactions = self.get("reactions", {})

    @loader.command(en_doc="- Add reaction [name | emoji]", ru_doc="- Добавить реакцию [имя | реакция]")
    async def addreact(self, message: Message):
        args = utils.get_args(message)

        if not args or len(args) < 2:
            await utils.answer(message, self.strings("incorrect_format"))
            return

        name = args[0]
        emoji = message.entities[0].document_id if message.entities and isinstance(message.entities[0], MessageEntityCustomEmoji) else args[1]
        self.reactions.update({name: emoji})
        self.set("reactions", self.reactions)

        await utils.answer(message, self.strings("reaction_added").format(name, emoji))

    @loader.command(en_doc="- Remove reaction [name]", ru_doc="- Удалить реакцию [имя]")
    async def delreact(self, message: Message):
        args = utils.get_args(message)

        if not args:
            await utils.answer(message, self.strings("incorrect_format"))
            return

        name = args[0]

        if name not in self.reactions:
            await utils.answer(message, self.strings("not_found").format(name))
            return

        self.reactions.pop(name)
        self.set("reactions", self.reactions)

        await utils.answer(message, self.strings("reaction_removed").format(name))

    @loader.command(en_doc="- React to a message [name]", ru_doc="- Поставить реакцию на сообщение [имя]")
    async def react(self, message: Message):
        args = utils.get_args(message)
        reply = await message.get_reply_message()

        if not args:
            await utils.answer(message, self.strings("incorrect_format"))
            return

        if not reply:
            await utils.answer(message, self.strings("no_reply"))
            return

        name = args[0]

        if name not in self.reactions:
            await utils.answer(message, self.strings("not_found").format(name))
            return

        await utils.send_reaction(self._client, reply, self.reactions[name])

        if not self.config["silent"]:
            await utils.answer(message, self.strings("done"))
            await asyncio.sleep(0.3)

        await message.delete()

    @loader.command(en_doc="- List of available reactions", ru_doc="- Список доступных реакций")
    async def reactlist(self, message: Message):
        reactions_list = ''.join(f"<b>{k} |</b> {'<emoji document_id=' + str(v) + '>🙂</emoji>' if isinstance(v, int) else v}\n" for k, v in self.reactions.items()) if self.reactions else ''
        await utils.answer(message, self.strings("reactions_list").format(reactions_list))