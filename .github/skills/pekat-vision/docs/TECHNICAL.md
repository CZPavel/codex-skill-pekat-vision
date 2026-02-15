# TECHNICAL

## Scope
Repo pokryva pouze skill `pekat-vision`.
Zamer: robustni sablony a demo klienti pro PEKAT Vision bez nebezpecnych defaultu.

## Hlavni casti
- `scripts/code_module_template.py`: sablona `main(context, module_item=None)` s ochranou proti KeyError/IndexError.
- `scripts/rest_api_client_demo.py`: demo klient pro `/analyze_image`, `/analyze_raw_image`, `/ping`, `/stop`.
- `scripts/projects_manager_tcp_demo.py`: simple TCP priklady pro start/stop/status/switch.
- `scripts/add_libs_to_sys_path.py`: helper pro externi knihovny na PEKAT serveru.

## Bezpecne defaulty
- Pri chybejicich datech vratit bezpecne `return`, nepadat vyjimkou.
- U API/TCP volani mit timeout a osetreni chyb.
- Tajemstvi a klice nikdy neukladat do repozitare.
- Nasazeni na produkci delat az po explicitnim schvaleni.

## Testovatelnost
- `tests/test_code_module_smoke.py` overuje ze sablona bezi mimo PEKAT runtime.
- `tests/test_rest_api_client_demo.py` overuje parsovani odpovedi a stavbu URL.

## Troubleshooting
- Chybi `ContextBase64utf` nebo `ImageLen`: zkontrolovat `response_type` a `context_in_body`.
- Import knihoven selhava: overit ABI/OS kompatibilitu a cestu v `sys.path`.
- Projects Manager prikazy neodpovidaji: overit format prikazu konkretni instalace.
