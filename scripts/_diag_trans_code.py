import os
from pathlib import Path

import pyodbc
from project_core.config.env import load_project_env

load_project_env(Path("/app"))
c = pyodbc.connect(os.environ["ANALYTICS_DB_DSN_2"], timeout=60)
cur = c.cursor()

cur.execute(
    """
SELECT s.TRANS_CODE, COUNT(*) cnt
FROM STRANS s
WHERE s.TRAN_DATE >= '2026-07-01' AND s.TRAN_DATE < '2026-07-07'
  AND s.SKU_ID IN (SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355'))
GROUP BY s.TRANS_CODE
"""
)
print("STRANS gift TRANS_CODE:", cur.fetchall())

cur.execute(
    """
SELECT h.TRANS_CODE, COUNT(DISTINCT s.TRANS_NUM) bills
FROM STRANS s
JOIN TRANSHDR h ON s.TRANS_NUM = h.TRANS_NUM AND RTRIM(s.STK_ID) = RTRIM(h.STK_ID)
WHERE s.TRAN_DATE >= '2026-07-01' AND s.TRAN_DATE < '2026-07-07'
  AND s.SKU_ID IN (SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355'))
GROUP BY h.TRANS_CODE
"""
)
print("TRANSHDR via STK+TRANS_NUM:", cur.fetchall())

cur.execute(
    """
SELECT h.TRANS_CODE, COUNT(DISTINCT s.TRANS_NUM) bills
FROM STRANS s
JOIN TRANSHDR h ON s.TRANS_NUM = h.TRANS_NUM
WHERE s.TRAN_DATE >= '2026-07-01' AND s.TRAN_DATE < '2026-07-07'
  AND s.SKU_ID IN (SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355'))
GROUP BY h.TRANS_CODE
"""
)
print("TRANSHDR via TRANS_NUM only:", cur.fetchall())

cur.execute(
    """
SELECT TOP 10 TRANS_CODE, COUNT(*) cnt FROM STRANS
WHERE TRAN_DATE >= '2026-07-01' AND TRAN_DATE < '2026-07-07'
GROUP BY TRANS_CODE ORDER BY COUNT(*) DESC
"""
)
print("STRANS all codes top:", cur.fetchall())

cur.execute(
    """
SELECT TOP 5 s.TRANS_NUM, RTRIM(s.STK_ID), s.TRANS_CODE AS s_code,
       h.TRANS_CODE AS h_code, h.AMOUNT
FROM STRANS s
LEFT JOIN TRANSHDR h ON s.TRANS_NUM = h.TRANS_NUM AND RTRIM(s.STK_ID) = RTRIM(h.STK_ID)
WHERE s.TRAN_DATE >= '2026-07-01' AND s.TRAN_DATE < '2026-07-07'
  AND s.SKU_ID IN (SELECT SKU_ID FROM SKU_DEF WHERE SKU_CODE IN ('00030344','00030348','00030355'))
"""
)
print("sample gift join header:", cur.fetchall())
