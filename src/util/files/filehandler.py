import json
import os
from pathlib import Path
from src.objects.enums.gettype import GetType
from src.objects.enums.status import Status


class FileHandler:
	"""
	A class to facilitate interacting with the file system
	"""
	_root = Path(__file__).parents[3]
	_paths = {
		"resource_path": _root.joinpath("resources"),

		"active_sell_orders_updated": _root.joinpath("resources", "orders", "sell", "active", "updated", "active_sell_orders_updated.json"),
		"active_sell_orders_rolling": _root.joinpath("resources", "orders", "sell", "active"),
		"active_sell_orders_restart_info_rolling": _root.joinpath("resources", "orders", "sell", "active", "active_sell_orders_restart_info_rolling.json"),
		"active_sell_orders_to_be_processed": _root.joinpath("resources", "orders", "sell", "active", "to_be_processed", "active_sell_orders_to_be_processed.json"),
		"active_sell_orders_missed": _root.joinpath("resources", "orders", "sell", "active", "missed", "active_sell_orders_missed.json"),
		"active_sell_orders_missed_to_be_processed": _root.joinpath("resources", "orders", "sell", "active", "to_be_processed", "active_sell_orders_missed_to_be_processed.json"),
		"active_sell_orders_double_checked": _root.joinpath("resources", "orders", "sell", "active", "double_checked", "active_sell_orders_double_checked.json"),
		"active_sell_orders_double_checked_to_be_processed": _root.joinpath("resources", "orders", "sell", "active", "to_be_processed", "active_sell_orders_double_checked_to_be_processed.json"),
		"active_sell_orders_purchase_error": _root.joinpath("resources", "orders", "sell", "active", "purchase_error", "active_sell_orders_purchase_error.json"),
		"active_sell_orders_purchase_error_to_be_processed": _root.joinpath("resources", "orders", "sell", "active", "to_be_processed", "active_sell_orders_purchase_error_to_be_processed.json"),

		"cancelled_sell_orders_rolling": _root.joinpath("resources", "orders", "sell", "cancelled"),
		"cancelled_sell_orders_restart_info_rolling": _root.joinpath("resources", "orders", "sell", "cancelled", "cancelled_sell_orders_restart_info_rolling.json"),
		"cancelled_sell_orders_to_be_processed": _root.joinpath("resources", "orders", "sell", "cancelled", "to_be_processed", "cancelled_sell_orders_to_be_processed.json"),
		"cancelled_sell_orders_missed": _root.joinpath("resources", "orders", "sell", "cancelled", "missed", "cancelled_sell_orders_missed.json"),
		"cancelled_sell_orders_missed_to_be_processed": _root.joinpath("resources", "orders", "sell", "cancelled", "to_be_processed", "cancelled_sell_orders_missed_to_be_processed.json"),
		"cancelled_sell_orders_double_checked": _root.joinpath("resources", "orders", "sell", "cancelled", "double_checked", "cancelled_sell_orders_double_checked.json"),
		"cancelled_sell_orders_double_checked_to_be_processed": _root.joinpath("resources", "orders", "sell", "cancelled", "to_be_processed", "cancelled_sell_orders_double_checked_to_be_processed.json"),
		"cancelled_sell_orders_purchase_error": _root.joinpath("resources", "orders", "sell", "cancelled", "purchase_error", "cancelled_sell_orders_purchase_error.json"),
		"cancelled_sell_orders_purchase_error_to_be_processed": _root.joinpath("resources", "orders", "sell", "cancelled", "to_be_processed", "cancelled_sell_orders_purchase_error_to_be_processed.json"),

		"filled_sell_orders_rolling": _root.joinpath("resources", "orders", "sell", "filled"),
		"filled_sell_orders_restart_info_rolling": _root.joinpath("resources", "orders", "sell", "filled", "filled_sell_orders_restart_info_rolling.json"),
		"filled_sell_orders_to_be_processed": _root.joinpath("resources", "orders", "sell", "filled", "to_be_processed", "filled_sell_orders_to_be_processed.json"),
		"filled_sell_orders_missed": _root.joinpath("resources", "orders", "sell", "filled", "missed", "filled_sell_orders_missed.json"),
		"filled_sell_orders_missed_to_be_processed": _root.joinpath("resources", "orders", "sell", "filled", "to_be_processed", "filled_sell_orders_missed_to_be_processed.json"),
		"filled_sell_orders_double_checked": _root.joinpath("resources", "orders", "sell", "filled", "double_checked", "filled_sell_orders_double_checked.json"),
		"filled_sell_orders_double_checked_to_be_processed": _root.joinpath("resources", "orders", "sell", "filled", "to_be_processed", "filled_sell_orders_double_checked_to_be_processed.json"),
		"filled_sell_orders_purchase_error": _root.joinpath("resources", "orders", "sell", "filled", "purchase_error", "filled_sell_orders_purchase_error.json"),
		"filled_sell_orders_purchase_error_to_be_processed": _root.joinpath("resources", "orders", "sell", "filled", "to_be_processed", "filled_sell_orders_purchase_error_to_be_processed.json"),

		"inactive_sell_orders_rolling": _root.joinpath("resources", "orders", "sell", "inactive"),
		"inactive_sell_orders_restart_info_rolling": _root.joinpath("resources", "orders", "sell", "inactive", "inactive_sell_orders_restart_info_rolling.json"),
		"inactive_sell_orders_to_be_processed": _root.joinpath("resources", "orders", "sell", "inactive", "to_be_processed", "inactive_sell_orders_to_be_processed.json"),
		"inactive_sell_orders_missed": _root.joinpath("resources", "orders", "sell", "inactive", "missed", "inactive_sell_orders_missed.json"),
		"inactive_sell_orders_missed_to_be_processed": _root.joinpath("resources", "orders", "sell", "inactive", "to_be_processed", "inactive_sell_orders_missed_to_be_processed.json"),
		"inactive_sell_orders_double_checked": _root.joinpath("resources", "orders", "sell", "inactive", "double_checked", "inactive_sell_orders_double_checked.json"),
		"inactive_sell_orders_double_checked_to_be_processed": _root.joinpath("resources", "orders", "sell", "inactive", "to_be_processed", "inactive_sell_orders_double_checked_to_be_processed.json"),
		"inactive_sell_orders_purchase_error": _root.joinpath("resources", "orders", "sell", "inactive", "purchase_error", "inactive_sell_orders_purchase_error.json"),
		"inactive_sell_orders_purchase_error_to_be_processed": _root.joinpath("resources", "orders", "sell", "inactive", "to_be_processed", "inactive_sell_orders_purchase_error_to_be_processed.json"),

		"expired_sell_orders_rolling": _root.joinpath("resources", "orders", "sell", "expired"),
		"expired_sell_orders_restart_info_rolling": _root.joinpath("resources", "orders", "sell", "expired", "expired_sell_orders_restart_info_rolling.json"),
		"expired_sell_orders_to_be_processed": _root.joinpath("resources", "orders", "sell", "expired", "to_be_processed", "expired_sell_orders_to_be_processed.json"),
		"expired_sell_orders_missed": _root.joinpath("resources", "orders", "sell", "expired", "missed", "expired_sell_orders_missed.json"),
		"expired_sell_orders_missed_to_be_processed": _root.joinpath("resources", "orders", "sell", "expired", "to_be_processed", "expired_sell_orders_missed_to_be_processed.json"),
		"expired_sell_orders_double_checked": _root.joinpath("resources", "orders", "sell", "expired", "double_checked", "expired_sell_orders_double_checked.json"),
		"expired_sell_orders_double_checked_to_be_processed": _root.joinpath("resources", "orders", "sell", "expired", "to_be_processed", "expired_sell_orders_double_checked_to_be_processed.json"),
		"expired_sell_orders_purchase_error": _root.joinpath("resources", "orders", "sell", "expired", "purchase_error", "expired_sell_orders_purchase_error.json"),
		"expired_sell_orders_purchase_error_to_be_processed": _root.joinpath("resources", "orders", "sell", "expired", "to_be_processed", "expired_sell_orders_purchase_error_to_be_processed.json"),


		"active_buy_orders_updated": _root.joinpath("resources", "orders", "buy", "active", "updated", "active_buy_orders_updated.json"),
		"active_buy_orders_rolling": _root.joinpath("resources", "orders", "buy", "active"),
		"active_buy_orders_restart_info_rolling": _root.joinpath("resources", "orders", "buy", "active", "active_buy_orders_restart_info_rolling.json"),
		"active_buy_orders_to_be_processed": _root.joinpath("resources", "orders", "buy", "active", "to_be_processed", "active_buy_orders_to_be_processed.json"),
		"active_buy_orders_missed": _root.joinpath("resources", "orders", "buy", "active", "missed", "active_buy_orders_missed.json"),
		"active_buy_orders_missed_to_be_processed": _root.joinpath("resources", "orders", "buy", "active", "to_be_processed", "active_buy_orders_missed_to_be_processed.json"),
		"active_buy_orders_double_checked": _root.joinpath("resources", "orders", "buy", "active", "double_checked", "active_buy_orders_double_checked.json"),
		"active_buy_orders_double_checked_to_be_processed": _root.joinpath("resources", "orders", "buy", "active", "to_be_processed", "active_buy_orders_double_checked_to_be_processed.json"),
		"active_buy_orders_purchase_error": _root.joinpath("resources", "orders", "buy", "active", "purchase_error", "active_buy_orders_purchase_error.json"),
		"active_buy_orders_purchase_error_to_be_processed": _root.joinpath("resources", "orders", "buy", "active", "to_be_processed", "active_buy_orders_purchase_error_to_be_processed.json"),

		"cancelled_buy_orders_rolling": _root.joinpath("resources", "orders", "buy", "cancelled"),
		"cancelled_buy_orders_restart_info_rolling": _root.joinpath("resources", "orders", "buy", "cancelled", "cancelled_buy_orders_restart_info_rolling.json"),
		"cancelled_buy_orders_to_be_processed": _root.joinpath("resources", "orders", "buy", "cancelled", "to_be_processed", "cancelled_buy_orders_to_be_processed.json"),
		"cancelled_buy_orders_missed": _root.joinpath("resources", "orders", "buy", "cancelled", "missed", "cancelled_buy_orders_missed.json"),
		"cancelled_buy_orders_missed_to_be_processed": _root.joinpath("resources", "orders", "buy", "cancelled", "to_be_processed", "cancelled_buy_orders_missed_to_be_processed.json"),
		"cancelled_buy_orders_double_checked": _root.joinpath("resources", "orders", "buy", "cancelled", "double_checked", "cancelled_buy_orders_double_checked.json"),
		"cancelled_buy_orders_double_checked_to_be_processed": _root.joinpath("resources", "orders", "buy", "cancelled", "to_be_processed", "cancelled_buy_orders_double_checked_to_be_processed.json"),
		"cancelled_buy_orders_purchase_error": _root.joinpath("resources", "orders", "buy", "cancelled", "purchase_error", "cancelled_buy_orders_purchase_error.json"),
		"cancelled_buy_orders_purchase_error_to_be_processed": _root.joinpath("resources", "orders", "buy", "cancelled", "to_be_processed", "cancelled_buy_orders_purchase_error_to_be_processed.json"),

		"filled_buy_orders_rolling": _root.joinpath("resources", "orders", "buy", "filled"),
		"filled_buy_orders_restart_info_rolling": _root.joinpath("resources", "orders", "buy", "filled", "filled_buy_orders_restart_info_rolling.json"),
		"filled_buy_orders_to_be_processed": _root.joinpath("resources", "orders", "buy", "filled", "to_be_processed", "filled_buy_orders_to_be_processed.json"),
		"filled_buy_orders_missed": _root.joinpath("resources", "orders", "buy", "filled", "missed", "filled_buy_orders_missed.json"),
		"filled_buy_orders_missed_to_be_processed": _root.joinpath("resources", "orders", "buy", "filled", "to_be_processed", "filled_buy_orders_missed_to_be_processed.json"),
		"filled_buy_orders_double_checked": _root.joinpath("resources", "orders", "buy", "filled", "double_checked", "filled_buy_orders_double_checked.json"),
		"filled_buy_orders_double_checked_to_be_processed": _root.joinpath("resources", "orders", "buy", "filled", "to_be_processed", "filled_buy_orders_double_checked_to_be_processed.json"),
		"filled_buy_orders_purchase_error": _root.joinpath("resources", "orders", "buy", "filled", "purchase_error", "filled_buy_orders_purchase_error.json"),
		"filled_buy_orders_purchase_error_to_be_processed": _root.joinpath("resources", "orders", "buy", "filled", "to_be_processed", "filled_buy_orders_purchase_error_to_be_processed.json"),

		"inactive_buy_orders_rolling": _root.joinpath("resources", "orders", "buy", "inactive"),
		"inactive_buy_orders_restart_info_rolling": _root.joinpath("resources", "orders", "buy", "inactive", "inactive_buy_orders_restart_info_rolling.json"),
		"inactive_buy_orders_to_be_processed": _root.joinpath("resources", "orders", "buy", "inactive", "to_be_processed", "inactive_buy_orders_to_be_processed.json"),
		"inactive_buy_orders_missed": _root.joinpath("resources", "orders", "buy", "inactive", "missed", "inactive_buy_orders_missed.json"),
		"inactive_buy_orders_missed_to_be_processed": _root.joinpath("resources", "orders", "buy", "inactive", "to_be_processed", "inactive_buy_orders_missed_to_be_processed.json"),
		"inactive_buy_orders_double_checked": _root.joinpath("resources", "orders", "buy", "inactive", "double_checked", "inactive_buy_orders_double_checked.json"),
		"inactive_buy_orders_double_checked_to_be_processed": _root.joinpath("resources", "orders", "buy", "inactive", "to_be_processed", "inactive_buy_orders_double_checked_to_be_processed.json"),
		"inactive_buy_orders_purchase_error": _root.joinpath("resources", "orders", "buy", "inactive", "purchase_error", "inactive_buy_orders_purchase_error.json"),
		"inactive_buy_orders_purchase_error_to_be_processed": _root.joinpath("resources", "orders", "buy", "inactive", "to_be_processed", "inactive_buy_orders_purchase_error_to_be_processed.json"),

		"expired_buy_orders_rolling": _root.joinpath("resources", "orders", "buy", "expired"),
		"expired_buy_orders_restart_info_rolling": _root.joinpath("resources", "orders", "buy", "expired", "expired_buy_orders_restart_info_rolling.json"),
		"expired_buy_orders_to_be_processed": _root.joinpath("resources", "orders", "buy", "expired", "to_be_processed", "expired_buy_orders_to_be_processed.json"),
		"expired_buy_orders_missed": _root.joinpath("resources", "orders", "buy", "expired", "missed", "expired_buy_orders_missed.json"),
		"expired_buy_orders_missed_to_be_processed": _root.joinpath("resources", "orders", "buy", "expired", "to_be_processed", "expired_buy_orders_missed_to_be_processed.json"),
		"expired_buy_orders_double_checked": _root.joinpath("resources", "orders", "buy", "expired", "double_checked", "expired_buy_orders_double_checked.json"),
		"expired_buy_orders_double_checked_to_be_processed": _root.joinpath("resources", "orders", "buy", "expired", "to_be_processed", "expired_buy_orders_double_checked_to_be_processed.json"),
		"expired_buy_orders_purchase_error": _root.joinpath("resources", "orders", "buy", "expired", "purchase_error", "expired_buy_orders_purchase_error.json"),
		"expired_buy_orders_purchase_error_to_be_processed": _root.joinpath("resources", "orders", "buy", "expired", "to_be_processed", "expired_buy_orders_purchase_error_to_be_processed.json"),

		"other_collections_folder": _root.joinpath("resources", "orders", "other_collections"),

		"timestamps_folder": _root.joinpath("resources", "logs", "timestamps"),

		"to_be_processed_downloaded_order_id_folder": _root.joinpath("resources", "logs","order_id", "to_be_processed"),
		"still_to_be_downloaded_order_ids_file": _root.joinpath("resources", "logs", "order_id", "still_to_be_downloaded", "still_to_be_downloaded_order_ids.json"),
		"last_downloaded_missing_order_id_file": _root.joinpath("resources", "logs", "order_id", "last_downloaded_missing_order_id.json"),
		"missed_order_ids_file": _root.joinpath("resources", "logs", "order_id", "missed_order_ids", "missed_order_ids.json"),

		"updated_active_sell_orders_timestamps_file": _root.joinpath("resources", "logs", "updated_active_ordes_timestamps", "sell", "updated_active_sell_orders_timestamps_file.json"),

		"processing_data_folder": _root.joinpath("resources", "processing_data"),
		"last_updated_timestamp_folder": _root.joinpath("resources", "processing_data", "last_updated_timestamp"),

		"response_error": _root.joinpath("resources", "logs", "errors", "response_error.json"),
		"request_error": _root.joinpath("resources", "logs", "errors", "request_error.json"),
		"too_many_api_calls": _root.joinpath("resources", "logs", "errors", "too_many_api_calls.json"),
		"internal_server_error": _root.joinpath("resources", "logs", "errors", "internal_server_error.json"),

		"processing_progress_log_file": _root.joinpath("resources", "logs", "progress", "processing_progress_log.json"),
		"download_progress_log_file": _root.joinpath("resources", "logs", "progress", "download_progress_log.json"),

		"stop_parallel_processing_file": _root.joinpath("resources", "logs", "stop", "stop_parallel_processing.json"),


		"filled_orders_timeline": _root.joinpath("resources", "filled_orders_timeline", "all_time_baseline"),
		"last_info_update": _root.joinpath("resources", "filled_orders_timeline", "all_time_baseline", "last_info_update.json"),

		"today_filled_orders_timeline": _root.joinpath("resources", "filled_orders_timeline", "today_baseline", "today_filled_orders_timeline.json"),

		"last_24_hours_sales": _root.joinpath("resources", "filled_orders_timeline", "sales", "last_24_hours"),
		"last_7_days_sales": _root.joinpath("resources", "filled_orders_timeline", "sales", "last_7_days"),
		"last_30_days_sales": _root.joinpath("resources", "filled_orders_timeline", "sales", "last_30_days"),

		"last_24_hours_price": _root.joinpath("resources", "filled_orders_timeline", "price", "last_24_hours"),
		"last_7_days_price": _root.joinpath("resources", "filled_orders_timeline", "price", "last_7_days"),
		"last_30_days_price": _root.joinpath("resources", "filled_orders_timeline", "price", "last_30_days"),

		"last_24_hours_price_change": _root.joinpath("resources", "filled_orders_timeline", "price_change", "last_24_hours"),
		"last_7_days_price_change": _root.joinpath("resources", "filled_orders_timeline", "price_change", "last_7_days"),
		"last_30_days_price_change": _root.joinpath("resources", "filled_orders_timeline", "price_change", "last_30_days"),

		"nordvpn_server_names": _root.joinpath("resources", "nordvpn", "nordvpn_server_names.json"),
		"server_up_time": _root.joinpath("resources", "nordvpn", "server_up_time.json"),
		"nordvpn_server_time_and_names": _root.joinpath("resources", "nordvpn", "nordvpn_server_time_and_names.json"),
		"nordvpn_server_names_austria": _root.joinpath("resources", "nordvpn", "nordvpn_server_names_austria.json"),
		"nordvpn_server_names_austria_time_and_names": _root.joinpath("resources", "nordvpn", "nordvpn_server_names_austria_time_and_names.json"),

		"double_checking_month_overview_folder": _root.joinpath("resources", "double_checking", "month_overview"),
		"double_checking_temp_timestamp_folder": _root.joinpath("resources", "double_checking", "temp_timestamp"),
		"current_month_to_be_double_checked_file": _root.joinpath("resources", "double_checking", "current_month_to_be_double_checked.json"),

		"potential_purchases":  _root.joinpath("resources", "potential_purchases"),

		"user_info_dic": _root.joinpath("resources", "bot_info", "user_info_dic.json"),
		"bot_info_dic": _root.joinpath("resources", "bot_info", "bot_info_dic.json"),

		"card_win_rate_rolling": _root.joinpath("resources", "win_rate", "cards", "rolling", "card_win_rate_rolling.json"),
		"card_win_rate_to_be_processed": _root.joinpath("resources", "win_rate", "cards", "to_be_processed", "card_win_rate_to_be_processed.json"),
		"card_win_rate_restart_info": _root.joinpath("resources", "win_rate", "cards", "card_win_rate_restart_info.json"),
		"months_overview_folder": _root.joinpath("resources", "win_rate", "cards", "months_overview"),

		"last_30_days_total_win_rate_file": _root.joinpath("resources", "win_rate", "cards", "created_information", "last_30_days_total_win_rate.json"),
		"last_30_days_mythic_win_rate_file": _root.joinpath("resources", "win_rate", "cards", "created_information", "last_30_days_mythic_win_rate.json"),

		"last_4_weekend_rank_total_win_rate_file": _root.joinpath("resources", "win_rate", "cards", "created_information", "last_4_weekend_rank_total_win_rate.json"),
		"last_4_weekend_rank_mythic_win_rate_file": _root.joinpath("resources", "win_rate", "cards", "created_information", "last_4_weekend_rank_mythic_win_rate.json"),

		"user_ranking_dic": _root.joinpath("resources", "win_rate", "user", "user_ranking_dic.json"),
		"to_be_processed_user_ranking_dic": _root.joinpath("resources", "win_rate", "user", "to_be_processed_user_ranking_dic.json"),

		"pk_info_file":  _root.joinpath("resources", "client_info", "pk_info.json"),
		"coinmarketcap_info_file":  _root.joinpath("resources", "client_info", "coinmarketcap_info.json"),
		"coinapi_info_file": _root.joinpath("resources", "client_info", "coinapi_info.json"),

		"sales_history": _root.joinpath("resources", "sales_history", "sales_history.csv"),

		"inventory_list": _root.joinpath("resources", "trading_info", "inventory", "inventory_list.json"),
		"competition_folder": _root.joinpath("resources", "trading_info", "competition"),
		"testing_info_file": _root.joinpath("resources", "trading_info", "testing_info", "testing_info.json"),

		"gods_unchained_original_assets": _root.joinpath("resources", "gu_assets", "gods_unchained_original_assets.json"),
		"gods_unchained_unknown_assets": _root.joinpath("resources", "gu_assets", "gods_unchained_unknown_assets.json"),

		"current_currency_prices": _root.joinpath("resources", "currency_assets", "current_currency_prices.json"),
		"historical_currency_prices": _root.joinpath("resources", "currency_assets", "historical_currency_prices.json"),

		"test_directory": _root.joinpath("resources", "test"),
		"test_file": _root.joinpath("resources", "test", "test_file.json"),
		"test_file_restart_info": _root.joinpath("resources", "test", "test_file_restart_info.json"),

	}

	def __init__(self):
		"""
		The constructor of the FileHandler class
		"""
		pass

	@classmethod
	def create_resources_folders(cls):
		"""
		A method to create the folder structure from scratch
		:return: None
		"""
		for str_path in cls._paths.values():

			path = Path(str_path)
			file_extension = path.suffix
			file_name = path.name
			directory_to_path = path.parent

			if file_extension:

				try:
					os.makedirs(directory_to_path)
				except FileExistsError:
					None

				if file_name == "pk_info.json":
					pk_info_dic = {}
					pk_info_dic["pk"] = ""
					pk_info_dic["sender"] = ""
					with open(path, 'w') as fp:
						fp.write(json.dumps(pk_info_dic, indent=4))

				elif file_name == "coinmarketcap_info.json":
					coinmarketcap_info_dic = {}
					coinmarketcap_info_dic["api_key"] = ""
					with open(path, 'w') as fp:
						fp.write(json.dumps(coinmarketcap_info_dic, indent=4))

				elif file_name == "coinapi_info_file.json":
					coinapi_info_dic = {}
					coinapi_info_dic["api_key"] = ""
					with open(path, 'w') as fp:
						fp.write(json.dumps(coinapi_info_dic, indent=4))

				elif file_extension == ".json":
					with open(path, 'w') as fp:
						fp.write("{}")
				else:
					with open(path, 'w') as fp:
						pass

			else:
				try:
					os.makedirs(path)
				except FileExistsError:
					None

	@classmethod
	def get_base_path(cls, path_of_interest):
		"""
		A method to get the path from the path dictionary
		:param path_of_interest: the key in the path dictionary
		:return: a path as a string
		"""
		return cls._paths[path_of_interest]

	@classmethod
	def get_store_path(cls, get_type, status, file_type):
		"""
		A method to get the path to store a kind of orders to
		:param get_type: the type of the orders i.e. buy
		:param status: the status of the orders i.e. active
		:param file_type: what kind of order it is i.e. double_checked_to_be_processed
		:return: a path as a string
		"""

		if isinstance(get_type, str):
			get_type = GetType[get_type.upper()]

		if isinstance(status, str):
			status = Status[status.upper()]

		search_string = status.name.lower() + "_" + get_type.name.lower() + "_orders_" + file_type.lower()
		return cls.get_base_path(search_string)

	@classmethod
	def get_latest_store_path(cls, get_type, request_type):
		"""
		A method to get the lastest file at which the orders were written down
		:param get_type: the type of order i.e. buy
		:param request_type: the status of the order
		:return: a path as a string
		"""
		base_store_path = cls.get_store_path(get_type, request_type)
		restart_info_path = cls.get_restart_info_path(get_type, request_type)

		if os.path.isfile(restart_info_path):
			with open(restart_info_path, 'r', encoding='utf-8') as restart_info_file:
				restart_dic = json.load(restart_info_file)
			restart_info_file.close()
			latest_split_file_number = restart_dic["latest_split_file_number"]
		else:
			latest_split_file_number = 0

		start_file_name = os.path.basename(os.path.splitext(base_store_path)[0])
		previous_directory = str(Path(base_store_path).parents[0])

		new_file_name = start_file_name + "_" + str(latest_split_file_number) + ".json"
		new_file_store_path = previous_directory + '\\' + new_file_name

		return new_file_store_path

	@classmethod
	def get_all_paths_of_get_type_and_status_orders(cls, get_type_str, status_str):
		"""
		A method to get all paths for orders of type and status
		:param get_type_str: the type of the order i.e. buy
		:param status_str: the status of the order i.e. active
		:return: the path as string
		"""

		overall_path_list = []

		rolling_path_list = FileHandler.get_all_paths_of_type_of_orders(get_type_str, status_str, "ROLLING")
		overall_path_list.extend(rolling_path_list)

		double_checked_file_path = FileHandler.get_store_path(get_type_str, status_str, "DOUBLE_CHECKED")
		overall_path_list.append(double_checked_file_path)

		# missed_file_path = File_Handler.get_store_path(get_type_str, status_str, "MISSED")
		# overall_path_list.append(missed_file_path)

		purchase_error_file_path = FileHandler.get_store_path(get_type_str, status_str, "PURCHASE_ERROR")
		overall_path_list.append(purchase_error_file_path)

		return overall_path_list

	@classmethod
	def get_all_paths_of_type_of_orders(cls, get_type_str, status_str, file_type):
		"""
		A method to get all paths of for orders of type, status and file_type
		:param get_type_str: the type of the order i.e. buy
		:param status_str: the status of the order i.e. active
		:param file_type: what kind of order it is i.e. double_checked_to_be_processed
		:return: a path as a string
		"""

		get_type = GetType[get_type_str]
		status = Status[status_str]

		base_store_path = cls.get_store_path(get_type, status, file_type)
		restart_info_path = cls.get_restart_info_path(get_type, status, file_type)

		if restart_info_path and os.path.isfile(restart_info_path):
			with open(restart_info_path, 'r', encoding='utf-8') as restart_info_file:
				restart_dic = json.load(restart_info_file)
			restart_info_file.close()
			latest_split_file_number = restart_dic["latest_split_file_number"]
		else:
			latest_split_file_number = 0

		start_file_name = status_str.lower() + "_" + get_type_str.lower() + "_orders_" + file_type.lower()

		latest_split_file_number = latest_split_file_number + 1
		path_list = []
		for number in range(latest_split_file_number):

			file_name = start_file_name + "_" + str(number) + ".json"
			file_store_path = str(base_store_path) + '\\' + file_name
			path_list.append(file_store_path)

		return path_list

	@classmethod
	def get_restart_info_path(cls, get_type, status, file_type):
		"""
		A method to get the restart info path
		:param get_type: the type of order i.e. type
		:param status: the status of the order i.e. active
		:param file_type: what kind of order it is i.e. double_checked_to_be_processed
		:return: a path as a string
		"""

		search_string = status.name.lower() + "_" + get_type.name.lower() + "_orders_restart_info_" + file_type.lower()
		return cls.get_base_path(search_string)
