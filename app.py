import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# 0. 내 제품 리스트 (상위 30개 탑재 완료)
# ---------------------------------------------------------
# 구조: "제품명": {"cost": 원가, "price": 정가(없으면 0), "discount": 할인율(없으면 0)}
MY_DATABASE = {
    "[DESK] THOMAS MASON OFFICE SHIRT": {"cost": 85892, "price": 0, "discount": 0},
    "[DESK] BASIC STEEL TIE [NAVY]": {"cost": 15992, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL V-NECK KNIT [BLACK]": {"cost": 42850, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL MOCK-NECK KNIT [CHARCOAL]": {"cost": 46238, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL V-NECK KNIT [CHARCOAL]": {"cost": 46238, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL V-NECK KNIT [DARK NAVY]": {"cost": 46238, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL V-NECK KNIT [DEEP BROWN]": {"cost": 46238, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL V-NECK KNIT [MELANGE GRAY]": {"cost": 46238, "price": 0, "discount": 0},
    "[DESK] GRAND CRU WOOL V-NECK KNIT [SILVER BLUE]": {"cost": 46238, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO JACKET [WASHED BLACK]": {"cost": 59290, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO JACKET [WASHED CHARCOAL]": {"cost": 72566, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO JACKET [WASHED NAVY]": {"cost": 88629, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO PANTS [LIGHT BEIGE]": {"cost": 61974, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO PANTS [WASHED BEIGE]": {"cost": 54329, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO PANTS [WASHED BLACK]": {"cost": 42561, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO PANTS [WASHED CHARCOAL]": {"cost": 51480, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO PANTS [WASHED KHAKI]": {"cost": 57475, "price": 0, "discount": 0},
    "[DESK] NATURAL CHINO PANTS [WASHED NAVY]": {"cost": 51480, "price": 0, "discount": 0},
    "[DESK] OFFICE HALF SHIRT [LIGHT BLUE]": {"cost": 29576, "price": 0, "discount": 0},
    "[DESK] OFFICE HALF SHIRT [LIGHT GRAY]": {"cost": 29576, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [DEEP CHARCOAL]": {"cost": 30962, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [FOG]": {"cost": 33393, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [GRAPHITE]": {"cost": 33393, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [GRAY]": {"cost": 33393, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [ICE BLUE]": {"cost": 30962, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [INK NAVY]": {"cost": 30962, "price": 0, "discount": 0},
    "[DESK] OFFICE SHIRT [WHITE]": {"cost": 33393, "price": 0, "discount": 0},
    "[DESK
