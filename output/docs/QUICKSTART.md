# Quick Start Guide - Payment Service Extraction

Get the payment service running in 5 minutes!

## Prerequisites

- Python 3.8+
- pip

## Step 1: Install Dependencies

```bash
# Install payment service dependencies
cd payment_service
pip install fastapi uvicorn pydantic pydantic-settings
cd ..

# Install shim layer dependencies (for monolith)
pip install requests
```

## Step 2: Start Payment Service

**Terminal 1:**
```bash
cd payment_service
python app.py
```

You should see:
```
============================================================
Payment Service v1.0.0 starting...
Service URL: http://0.0.0.0:8001
Payment Gateway: https://pay.internal.corp/api/v1/charge
Max Retries: 3
Currency: USD
Wire Minimum: $1000.0
============================================================
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8001
```

## Step 3: Test Payment Service

**Terminal 2:**
```bash
# Health check
curl http://localhost:8001/health

# Test card payment
curl -X POST http://localhost:8001/api/v1/payments/process \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-123" \
  -d '{
    "amount": 100.00,
    "currency": "USD",
    "method": "card",
    "card": {
      "number": "4111111111111111",
      "cvv": "123",
      "expiry": "12/26"
    }
  }'
```

Expected response:
```json
{
  "status": "ok",
  "transaction_id": "TXN1714574400",
  "amount": 100.0,
  "timestamp": "2026-05-01T16:00:00.000Z"
}
```

## Step 4: Run Monolith with Payment Service

**Terminal 3:**
```bash
# Enable payment service integration
export USE_PAYMENT_SERVICE="true"
export PAYMENT_SERVICE_URL="http://localhost:8001"
export PAYMENT_SERVICE_API_KEY="dev-api-key-123"

# Run monolith
python enterprise_monolith.py
```

You should see:
```
[INIT] Payment Service Integration: ENABLED
[INIT] Payment Service URL: http://localhost:8001
[INIT] Circuit Breaker: Active (threshold=5, timeout=60s)
```

## Step 5: Test Integration

The `bootstrap()` function will automatically:
1. Create test users
2. Add test products
3. Process a test order using the payment service
4. Display order confirmation

Look for these logs:
```
[INFO] Processing card payment for $1359.88
[INFO] Card payment successful: TXN1714574400
[ORDER RESULT] {
  "status": "ok",
  "oid": "ORD...",
  "txn": "TXN...",
  "total": 1359.88
}
```

## Step 6: Test Fallback (Optional)

Test circuit breaker and fallback:

1. **Stop payment service** (Ctrl+C in Terminal 1)
2. **Run monolith again** (Terminal 3)
3. **Observe fallback behavior:**

```
[PAYMENT-SERVICE-ERROR] Cannot connect to payment service
[FALLBACK] Payment service unavailable, using legacy logic
[PAY-LEGACY] POST https://pay.internal.corp/api/v1/charge
Circuit breaker: Opening circuit after 5 failures
```

## Step 7: Switch to Legacy Mode

To use legacy payment processing without the service:

```bash
# Disable payment service
export USE_PAYMENT_SERVICE="false"

# Run monolith
python enterprise_monolith.py
```

You should see:
```
[INIT] Payment Service Integration: DISABLED
[LEGACY-MODE] Using legacy payment processing
```

## API Documentation

Once the payment service is running, visit:
- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

## Troubleshooting

### Payment service won't start

**Error:** `Import "fastapi" could not be resolved`

**Solution:**
```bash
cd payment_service
pip install -r requirements.txt
```

### Monolith can't connect to service

**Error:** `[PAYMENT-SERVICE-ERROR] Cannot connect to payment service`

**Solution:**
1. Verify payment service is running: `curl http://localhost:8001/health`
2. Check `PAYMENT_SERVICE_URL` environment variable
3. Ensure port 8001 is not blocked

### Authentication errors

**Error:** `Payment service authentication failed`

**Solution:**
1. Verify API key matches: `dev-api-key-123`
2. Check `X-API-Key` header is being sent
3. Review payment service logs

## What's Next?

✅ Payment service is running
✅ Monolith is integrated
✅ Circuit breaker is active
✅ Fallback is working

**Next steps:**
1. Review [`README_PAYMENT_EXTRACTION.md`](README_PAYMENT_EXTRACTION.md) for detailed documentation
2. Review [`strangler_fig_payment_extraction_plan.md`](strangler_fig_payment_extraction_plan.md) for architecture
3. Review [`domain_analysis.md`](domain_analysis.md) for original coupling analysis
4. Deploy to staging environment
5. Begin gradual traffic migration

## Key Files

- **Payment Service:** `payment_service/app.py`
- **Monolith Integration:** `enterprise_monolith.py` (lines 1-60, 294-480)
- **Shim Layer:** `shim/payment_client.py`, `shim/circuit_breaker.py`, `shim/fallback_handler.py`
- **Configuration:** Environment variables

## Success Indicators

✅ Payment service responds to health checks
✅ Monolith can process orders through service
✅ Circuit breaker triggers fallback when service is down
✅ Legacy mode works without service
✅ No errors in logs during normal operation

## Support

For detailed information:
- Architecture: [`strangler_fig_payment_extraction_plan.md`](strangler_fig_payment_extraction_plan.md)
- Operations: [`README_PAYMENT_EXTRACTION.md`](README_PAYMENT_EXTRACTION.md)
- Analysis: [`domain_analysis.md`](domain_analysis.md)