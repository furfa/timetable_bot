
@dp.message_handler(ChatTypeFilter('private'), state="*")
async def handle_creation(message : types.Message, state : FSMContext):
    raw_text = message.text
    fields = raw_text