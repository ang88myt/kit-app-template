# Warehouse Digital-Twin Data-Layer APIs

- Host: https://digital-twin.expangea.com
- Required request header: **X-API-KEY**


## **Warehouse**

### Warehouse API
- Endpoint: ``` /warehouse/```
- Method: POST

### Warehouse Details API
- Endpoint: ``` /warehouse/<warehouse_code>/```
- Method: POST

## **Rack**

### Rack List API
- Endpoint: ``` /rack/<warehouse_code>/<floor_no>/```
- Method: POST

### Rack Details API
- Endpoint: ``` /rack/<warehouse_code>/<floor_no>/<rack_no>/```
- Method: POST

### Rack Location Details API
- Endpoint: ``` /rack-location/<location_id>/```
- Method: POST

## Rack Location Upload API
- Endpoint: /upload-rack-location/
- Method: POST
- Payload: [
    {
        "warehouse": string,
        "floor_no": number,
        "rack_no": number,
        "location_id": string,
        "x": number,
        "y": number,
        "z": number,
-     },
-    . . .
- ]

### Pallet Details API
- Endpoint: ``` /pallet/<pallet_id>/```
- Method: POST

### Pallet History API
- Endpoint: ``` /pallet/<pallet_id>/<days>/```
- Method: POST

## **Device Location**

### Device Location API
- Endpoint: ``` /device/<device-name>/```
- Method: POST

### Device Location History API
- Endpoint: ``` /device/<device-name>/<days>/```
- Method: POST

### Device Location Upload API
- Endpoint: ``` /device/```
- Method: POST
- Payload: {
    name: string,
    position: {
        x: number,
        y: number,
        z: number,
    }
}


### Floor Location API
- Endpoint: ```/floor-location/<warehouse_code>/<floor_no>/<x>/<y>/```
- Method: POST

## **Pallet Expiry APIs**
- Method: POST
- Expiry at current date
- Endpoint: /expiry/<warehouse_code>/<floor_no>/<rack-no>/
- Endpoint: /expiry/<warehouse_code>/<floor_no>/
- Endpoint: /expiry/<warehouse_code>/

### Expiry at specified date
- Endpoint: /expiry/<warehouse_code>/<floor_no>/<rack-no>/?date=yyyy-mm-dd
- Endpoint: /expiry/<warehouse_code>/<floor_no>/?date=yyyy-mm-dd
- Endpoint: /expiry/<warehouse_code>/?date=yyyy-mm-dd

### Expiry at between two dates
- Endpoint: /expiry/<warehouse_code>/<floor_no>/<rack-no>/?from=yyyy-mm-dd&date=yyyy-mm-dd
- Endpoint: /expiry/<warehouse_code>/<floor_no>/?from=yyyy-mm-dd&date=yyyy-mm-dd
- Endpoint: /expiry/<warehouse_code>/?from=yyyy-mm-dd&date=yyyy-mm-dd
