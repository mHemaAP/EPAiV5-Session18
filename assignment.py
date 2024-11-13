import json
from datetime import date, datetime
from decimal import Decimal

class Stock:
    def __init__(self, symbol, date, open_, high, low, close, volume):
        self.symbol = symbol
        self.date = date
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        
class Trade:
    def __init__(self, symbol, timestamp, order, price, volume, commission):
        self.symbol = symbol
        self.timestamp = timestamp
        self.order = order
        self.price = price
        self.commission = commission
        self.volume = volume

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Stock):
            return {
                "__type__": "Stock",
                "symbol": obj.symbol,
                "date": obj.date.isoformat(),
                "open": str(obj.open),
                "high": str(obj.high),
                "low": str(obj.low),
                "close": str(obj.close),
                "volume": obj.volume
            }
        elif isinstance(obj, Trade):
            return {
                "__type__": "Trade",
                "symbol": obj.symbol,
                "timestamp": obj.timestamp.isoformat(),
                "order": obj.order,
                "price": str(obj.price),
                "volume": obj.volume,
                "commission": str(obj.commission)
            }
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def custom_decoder(obj_dict):
    if "__type__" not in obj_dict:
        return obj_dict
        
    obj_type = obj_dict["__type__"]
    if obj_type == "Stock":
        return Stock(
            symbol=obj_dict["symbol"],
            date=date.fromisoformat(obj_dict["date"]),
            open_=Decimal(obj_dict["open"]),
            high=Decimal(obj_dict["high"]),
            low=Decimal(obj_dict["low"]),
            close=Decimal(obj_dict["close"]),
            volume=obj_dict["volume"]
        )
    elif obj_type == "Trade":
        return Trade(
            symbol=obj_dict["symbol"],
            timestamp=datetime.fromisoformat(obj_dict["timestamp"]),
            order=obj_dict["order"],
            price=Decimal(obj_dict["price"]),
            volume=obj_dict["volume"],
            commission=Decimal(obj_dict["commission"])
        )
    return obj_dict


from marshmallow import Schema, fields, post_load

class StockSchema(Schema):
    symbol = fields.Str()
    date = fields.Date()
    # open = fields.Decimal()
    open = fields.Decimal(data_key='open_')  # Changed to match Stock.__init__    
    high = fields.Decimal()
    low = fields.Decimal()
    close = fields.Decimal()
    volume = fields.Integer()

    @post_load
    def make_stock(self, data, **kwargs):
        # Ensure we use open_ in the data
        if 'open' in data:
            data['open_'] = data.pop('open')
        return Stock(**data)

class TradeSchema(Schema):
    symbol = fields.Str()
    timestamp = fields.DateTime()
    order = fields.Str()
    price = fields.Decimal()
    volume = fields.Integer()
    commission = fields.Decimal()

    @post_load
    def make_trade(self, data, **kwargs):
        return Trade(**data)

def serialize_with_marshmallow(obj):
    if isinstance(obj, Stock):
        # Convert to dict first, then use custom JSON encoder
        stock_dict = StockSchema().dump(obj)
        return json.dumps(stock_dict, cls=CustomEncoder)        
        # return StockSchema().dumps(obj)
    elif isinstance(obj, Trade):
        trade_dict = TradeSchema().dump(obj)
        return json.dumps(trade_dict, cls=CustomEncoder)
        # return TradeSchema().dumps(obj)
    raise ValueError("Unsupported type for serialization")

def deserialize_with_marshmallow(json_str, schema):
    # return schema.loads(json_str)
    # Parse JSON string to dict first
    data_dict = json.loads(json_str)
    return schema.load(data_dict)    