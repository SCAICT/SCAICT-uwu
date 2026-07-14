"""
enum 測試
"""

# Standard imports
import enum


class GiftType(enum.Enum):
    point = "電電點"
    ticket = "抽獎券"


for gt in GiftType:  # equal to print(GiftType.{item}.name)
    print(gt)

print(GiftType.point.name)

print(GiftType.point.value)
