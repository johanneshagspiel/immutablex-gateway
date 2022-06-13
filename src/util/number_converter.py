from objects.currency.currency import Currency


class Number_Converter():

    def __init__(self):
        None

    @staticmethod
    def get_next_cheapest_number(number_str):

        quantization_length = 10

        split_number = list(number_str)

        if '.' in split_number:
            part_before_point = list(number_str.split('.')[0])
            part_after_point = list(number_str.split('.')[1])

            if len(part_after_point) > quantization_length:
                part_after_point = part_after_point[:quantization_length]

                temp_number = "".join(part_before_point) + "." + "".join(part_after_point)
                split_number = list(temp_number)

            point_index = split_number.index('.')
            split_number.pop(point_index)

        else:
            point_index = len(number_str)

        split_number.reverse()

        decreased_number_list = []
        least_significant_position_found = False
        least_significant_position = None
        for index, position in enumerate(split_number):
            if position != '0':
                if least_significant_position_found == False:
                    least_significant_position_found = True
                    decreased_number = int(position) - 1
                    decreased_number_list.append(str(decreased_number))
                    least_significant_position = index
                else:
                    decreased_number_list.append(position)
            else:
                decreased_number_list.append(position)

        new_number_list = []
        for index, position in enumerate(decreased_number_list):
            if index < least_significant_position:
                new_number_list.append('9')
            else:
                new_number_list.append(position)

        new_number_list.reverse()

        new_number_list.insert(point_index, '.')
        new_number = "".join(new_number_list)

        part_before_point = list(new_number.split('.')[0])
        part_after_point = list(new_number.split('.')[1])

        if len(part_after_point) < quantization_length:
            nines_to_add = quantization_length - len(part_after_point)

            for nine_to_add in range(nines_to_add):
                part_after_point.append(str(9))

            new_number = "".join(part_before_point) + "." + "".join(part_after_point)

        else:
            part_after_point = part_after_point[:quantization_length]
            new_number = "".join(part_before_point) + "." + "".join(part_after_point)

        return new_number


    @staticmethod
    def quantize_number_str(price_floor_in_crypto):

        quantum = 10

        split_number = list(str(price_floor_in_crypto))

        if 'e' in split_number:
            e_position = 0
            for index, letter in enumerate(split_number):
                if letter == "e":
                    e_position = index
                    before_list = split_number[:e_position]
                    after_list = split_number[(e_position + 2):]
                    number_of_shifts = int("".join(after_list))

                    new_letter_list = []
                    for letter in before_list:
                        if letter != '.':
                            new_letter_list.append(letter)

                    for shift in range(number_of_shifts):
                        new_letter_list.insert(0, '0')
                    new_letter_list.insert(1, '.')

            split_number = new_letter_list
            price_floor_in_crypto = "".join(split_number)

        part_before_point = list(str(price_floor_in_crypto).split('.')[0])
        part_after_point = list(str(price_floor_in_crypto).split('.')[1])

        if len(part_after_point) > quantum:
            part_after_point_new = part_after_point[:quantum]
            last_letter = part_after_point_new[-1]

            number_after_last_letter = int(part_after_point[quantum])
            if number_after_last_letter >= 5:
                changed_number = str(int(last_letter) + 1)
            else:
                changed_number = last_letter

            part_after_point_new[-1] = changed_number
            part_after_point = part_after_point_new

        final_number = "".join(part_before_point) + '.' + "".join(part_after_point)

        return final_number

    @staticmethod
    def get_float_str_from_quantity_decimal(quantity, decimals):
        new_number_list = Number_Converter._convert_quantity_decimal_to_list(quantity, decimals)
        final_number = "".join(new_number_list)

        before_decimal = final_number.split('.')[0]
        after_decimal = final_number.split('.')[1]
        if len(after_decimal) >= 18:
            after_decimal = after_decimal[:17]

        final_number = "".join(before_decimal) + '.' + "".join(after_decimal)

        return final_number

    @staticmethod
    def get_float_from_quantity_decimal(quantity, decimals):
        new_number_list = Number_Converter._convert_quantity_decimal_to_list(quantity, decimals)
        final_number = float("".join(new_number_list))
        return final_number

    @staticmethod
    def _convert_quantity_decimal_to_list(quantity, decimals):
        split_number = list(str(quantity))

        if 'e' in split_number:
            for index, letter in enumerate(split_number):
                if letter == "e":
                    e_position = index
                    before_list = split_number[:e_position]
                    after_list = split_number[(e_position + 2):]
                    number_of_shifts = int("".join(after_list))
                    new_number_of_shifts = number_of_shifts

                    seen_period = False
                    new_letter_list = []
                    for letter in before_list:
                        if letter != '.':
                            new_letter_list.append(letter)
                            if seen_period:
                                new_number_of_shifts = new_number_of_shifts - 1
                        else:
                            seen_period = True

                    for additional_zero in range(new_number_of_shifts):
                        new_letter_list.append('0')

                    split_number = new_letter_list

        elif '.' in split_number:
            split_number = list(str(quantity).split('.')[0])

        len_number = len(split_number)

        point_position = len_number - decimals

        if point_position > 0:
            split_number.insert(point_position, '.')

        else:
            split_number.insert(0, '0')
            split_number.insert(1, '.')

            point_position = -1 * point_position

            for zero in range(point_position):
                split_number.insert(2, '0')

        return split_number


    @staticmethod
    def get_quantity_decimal_from_float(float_number, currency_str):

        split_number = list(str(float_number))

        if 'e' in split_number:
            e_position = 0
            for index, letter in enumerate(split_number):
                if letter == "e":
                    e_position = index
                    before_list = split_number[:e_position]
                    after_list =  split_number[(e_position+2):]
                    number_of_shifts = int("".join(after_list))

                    new_letter_list = []
                    for letter in before_list:
                        if letter != '.':
                            new_letter_list.append(letter)

                    for shift in range(number_of_shifts):
                        new_letter_list.insert(0, '0')
                    new_letter_list.insert(1, '.')

            split_number = new_letter_list

        currency = Currency[currency_str]

        if currency == Currency.ETH:
            decimal = 18
        elif currency == Currency.GODS:
            decimal = 18
        elif currency == Currency.IMX:
            decimal = 18
        elif currency == Currency.USDC:
            decimal = 6
        elif currency == Currency.GOG:
            decimal = 18
        elif currency == Currency.OMI:
            decimal = 18

        has_seen_dot = False
        has_seen_not_0 = False
        has_seen_not_0_before_dot = False
        after_dot_count = 0
        new_number_list = []

        for letter in split_number:

            if (letter != '0') and (letter != '.'):
                has_seen_not_0 = True

                if has_seen_dot == False:
                    has_seen_not_0_before_dot = True

            if has_seen_not_0:
                if letter != '.':
                    new_number_list.append(letter)

            if has_seen_dot or has_seen_not_0:
                if letter != '.':
                    after_dot_count = after_dot_count + 1

            if letter == '.':
                has_seen_dot = True

        still_to_fill = decimal - after_dot_count

        if has_seen_not_0_before_dot:
            still_to_fill = still_to_fill + 1

        for to_fill in range(still_to_fill):
            new_number_list.append('0')

        try:
            quantity = int("".join(new_number_list))

        except Exception as e:
            print(" ")
            print("Error")
            print(new_number_list)
            print(before_list)
            print(new_letter_list)
            print(float_number)
            print(" ")
            quantity = None

        return (quantity, decimal)