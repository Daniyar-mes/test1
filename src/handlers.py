from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .keyboards import confirm_inline_keyboard

router = Router()


users_data = {}


class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_confirmation = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(f"Привет, {message.from_user.full_name}!")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        f"/start - Приветствие\n"
        f"/help - Список доступных команд\n"
        f"/register - Пройти регистрацию\n"
        f"/profile - Посмотреть свой профиль"
    )
 

@router.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext):
    await message.answer("Шаг 1: Введите ваше имя:")
    await state.set_state(Registration.waiting_for_name)


@router.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Шаг 2: Введите ваш возраст:")
    await state.set_state(Registration.waiting_for_age)


@router.message(Registration.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Это не число! Пожалуйста, введите возраст цифрами:")
        return

    age = int(message.text)
    
    if age <= 0:
        await message.answer("Возраст должен быть больше нуля! Пожалуйста, введите возраст цифрами:")
        return

    await state.update_data(age=age)
    
    
    data = await state.get_data()
    
    await message.answer(
        f"Проверьте ваши данные:\n"
        f"Имя: {data['name']}\n"
        f"Возраст: {data['age']}",
        reply_markup=confirm_inline_keyboard
    )
    await state.set_state(Registration.waiting_for_confirmation)


@router.callback_query(Registration.waiting_for_confirmation, F.data == "confirm_reg")
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    

    users_data[user_id] = {
        "name": data["name"],
        "age": data["age"]
    }
    
    await callback.answer()
    await callback.message.answer("Регистрация завершена!")
    await state.clear()

@router.callback_query(Registration.waiting_for_confirmation, F.data == "restart_reg")
async def restart_registration(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Начнем заново. Шаг 1: Введите ваше имя:")
    await state.set_state(Registration.waiting_for_name)


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user_id = message.from_user.id
    
    if user_id in users_data:
        user = users_data[user_id]
        await message.answer(
            f"Ваши данные:\n"
            f"Имя — {user['name']}\n"
            f"Возраст — {user['age']}"
        )
    else:
        await message.answer("Вы не зарегистрированы. Напишите /register, чтобы пройти регистрацию.")
