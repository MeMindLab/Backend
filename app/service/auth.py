import phonenumbers


def normalize_phone_number(phone: str) -> str:
    try:
        # 입력된 전화번호 파싱
        parsed_number = phonenumbers.parse(phone, "KR")
        # 국가 코드를 포함한 형식으로 포맷팅
        formatted_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.E164
        )
        return formatted_number
    except phonenumbers.phonenumberutil.NumberParseException:
        # 파싱 실패 시 예외 처리
        raise ValueError("Invalid phone number format")
