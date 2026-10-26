# CDSCO NSQ / Spurious Drug Alert Data Sources: URL-level inventory (as of 25 Oct 2026)

Scope: every source StripCheck can ingest for CDSCO "Not of Standard Quality" (NSQ) and spurious drug alerts: legacy monthly PDFs (Jan 2024 to mid-2025), the NSQ portal used since Aug 2025, press and third-party mirrors (Aug 2025 to Oct 2026), state drug-controller lists, open datasets and scrapers, and CDSCO reuse terms. Method: WebFetch and WebSearch only, no browser. Reachability legend used in the tables:
- **V**: fetched by WebFetch on 25 Oct 2026 and the PDF/JSON came back.
- **E**: fetched by WebFetch, empty body returned.
- **L**: link listed on the official CDSCO Alerts page (not fetched individually).
- **I**: URL exists in a search-engine index (not fetched individually).
- **M**: listed on a mirror's index page (not fetched individually).

---

## Q1. Legacy CDSCO monthly NSQ / spurious alert PDFs, Jan 2024 to mid-2025 (exact URLs, level, kind, reachability)

### Takeaway
The official CDSCO Drug Alerts page lists every monthly list from Dec 2023 to June 2025 as `download_file_division.jsp?num_id=<base64 integer>` links. Central-lab and state-lab lists are separate from May 2024, and separate spurious lists exist for Apr 2024 and from Aug 2024. The last PDF months on that page are June 2025 (released 18 Jul 2025) and a revised May 2025 list. No July 2025 entry is listed there, although a mirror holds July 2025 PDFs. Direct `UploadAlertsFiles/<name>.pdf` URLs were confirmed for 15 lists, two of them fetched live. TheHealthMaster mirrors almost every month as PDF.

### Cited Findings

**How the official index works**
- Index page: https://cdsco.gov.in/opencms/opencms/en/Notifications/Alerts/ lists about 300 entries from 2010 to 2026 on one page, with no pagination. Each file link is a relative href of the form `/opencms/opencms/system/modules/CDSCO.WEB/elements/download_file_division.jsp?num_id=...`. The page also links a new "NSQ Alerts" item (badge "New") at `/opencms/opencms/en/Notifications/nsq-drugs/`. [CDSCO Alerts](https://cdsco.gov.in/opencms/opencms/en/Notifications/Alerts/)
- A second CDSCO listing exists at https://cdsco.gov.in/opencms/opencms/en/Latest-Alerts/. Its search-cached copy ends at the 28 Aug 2025 notice "Availability of Not Standard Quality (NSQ) Alert on New Link in CDSCO Website". [CDSCO Latest Alerts](https://cdsco.gov.in/opencms/opencms/en/Latest-Alerts/)
- The direct file store is `https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/`. File names are irregular: mixed case, double spaces, "JUly", "Sept", "(2)". [search index of UploadAlertsFiles](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/NSQ%20ALERT%20FOR%20THE%20MONTH%20OF%20JUly-2024.pdf)
- The same store is also indexed under the host `cdsco.mohfw.gov.in` (October 2024 file). [cdsco.mohfw.gov.in copy](https://cdsco.mohfw.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/NSQ%20ALERT%20FOR%20THE%20MONTH%20OF%20OCTOBER-2024.pdf)
- When fetched by WebFetch, the JSP links for June 2025 NSQ (`num_id=MTI5Mjc=`) and the 28 Aug 2025 notice (`num_id=MTMyNDU=`) both returned an empty body. [JSP June 2025](https://cdsco.gov.in/opencms/opencms/system/modules/CDSCO.WEB/elements/download_file_division.jsp?num_id=MTI5Mjc=)
- An independent scraper README states that "CDSCO's download links don't return the PDF directly." Its downloader saves non-PDF responses to `data/raw/not_pdf/` and stores the resolved file address as `pdf_url`. [Swa-hub/nsq-medicine-tracker](https://github.com/Swa-hub/nsq-medicine-tracker)
- Two direct PDFs were fetched live on 25 Oct 2026:
  - `NSQ ALERT MAY-2025.pdf`: 196.8 KB, 7 pages, A4 landscape, Arial fonts with ToUnicode, so a text layer is likely. [May 2025 NSQ PDF](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/NSQ%20ALERT%20MAY-2025.pdf)
  - `List of spurious Drugs June-2025.pdf`: 126.8 KB, 2 pages, created 2025-07-18 with Microsoft Word 2019. [June 2025 spurious PDF](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/List%20of%20spurious%20Drugs%20June-2025.pdf)
- The central list for July 2024 opens with the heading "A. CDSCO/Central Laboratories". The June 2025 state list says its data came from the State Drugs Licensing Authorities of HP, Jharkhand, Karnataka, Maharashtra, Punjab, Tamil Nadu, Telangana, Tripura, West Bengal (Nil), Puducherry, J&K, Ladakh (Nil) and others. [July 2024 PDF](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/NSQ%20ALERT%20FOR%20THE%20MONTH%20OF%20JUly-2024.pdf); [June 2025 State PDF](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/STATE%20NSQ%20%20June%20-2025.pdf)
- A CDSCO guidance document mirrored by Medical Dialogues asks state and central labs to submit NSQ reports, with a copy of the test report, "preferably before 10th of every month for uploading at CDSCO website" (wording as shown in the search snippet). [MD pdf_upload guidance](https://medicaldialogues.in/pdf_upload/cdsco-guidance-document-254723.pdf)

**Table A: official monthly lists, Jan 2024 to Jul 2025**

JSP = `https://cdsco.gov.in/opencms/opencms/system/modules/CDSCO.WEB/elements/download_file_division.jsp?num_id=` + the value shown. UAF = `https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/`. All titles and release dates are as listed on the [CDSCO Alerts page](https://cdsco.gov.in/opencms/opencms/en/Notifications/Alerts/). The decoded ID is my base64 decode of `num_id`.

| Month | Level | Kind | CDSCO title (release date) | JSP num_id (decoded) | Direct UAF PDF (if found) | Reach |
|---|---|---|---|---|---|---|
| 2024-01 | combined | NSQ | Drug Alert for the Month of January 2024 (2024-02-21) | `MTA5Mzk=` (10939) | not found | L |
| 2024-01 | combined | NSQ revised | Drug Alert for the Month of Revised Jan 2024 (2024-03-20) | `MTEwMTQ=` (11014) | not found | L |
| 2024-02 | combined | NSQ | Drug Alert for the Month of February 2024 (2024-03-20) | `MTEwMTM=` (11013) | not found | L |
| 2024-03 | combined | NSQ | Drug Alert for the Month of March 2024 (2024-04-16) | `MTExMTU=` (11115) | not found | L |
| 2024-04 | combined | NSQ | NOT OF STANDARD QUALITY ALERT FOR THE MONTH OF APRIL 2024 (2024-05-17) | `MTEyNTY=` (11256) | UAF`Drug%20NSQ%20Alert%20April%202024.pdf` (11 pages per index) | L, I |
| 2024-04 | central | spurious | SPURIOUS ALERT FOR THE MONTH OF APRIL 2024 (2024-05-17) | `MTEyNTU=` (11255) | not found | L |
| 2024-05 | central | NSQ | NSQ May 2024 CDSCO Labs (2024-06-20) | `MTEzNzI=` (11372) | not found | L |
| 2024-05 | state | NSQ | NSQ May 2024 State Labs (2024-06-20) | `MTEzNzM=` (11373) | not found | L |
| 2024-06 | central | NSQ | NSQ ALERT FOR THE MONTH OF JUNE 2024 (2024-07-19) | `MTE0Njg=` (11468) | not found | L |
| 2024-06 | state | NSQ | State NSQ ALERT FOR THE MONTH OF JUNE 2024 (2024-07-19) | `MTE0Njc=` (11467) | not found | L |
| 2024-07 | central | NSQ | NSQ ALERT FOR THE MONTH OF JUlY-2024 (2024-08-22) | `MTE2MDA=` (11600) | UAF`NSQ%20ALERT%20FOR%20THE%20MONTH%20OF%20JUly-2024.pdf` | L, I |
| 2024-07 | state | NSQ | STATE NSQ ALERT FOR THE MONTH OF July-2024 (2024-08-22) | `MTE2MDE=` (11601) | not found | L |
| 2024-08 | central | NSQ | Drug Alert for the Month of August 2024 (2024-09-20) | `MTIwMTA=` (12010) | UAF`alert%20August-2024.pdf` | L, I |
| 2024-08 | state | NSQ | State Drug Alert for the Month of August 2024 (2024-09-20) | `MTIwMTI=` (12012) | not found | L |
| 2024-08 | central | spurious/adulterated/misbranded | List of ... declared as Spurious Adulterated Misbranded ... August-2024 (2024-09-20) | `MTIwMTE=` (12011) | not found | L |
| 2024-09 | central | NSQ | Drug Alert for the Month of September 2024 (2024-10-24) | `MTIwODQ=` (12084) | UAF`NSQ%20Alert%20For%20the%20month%20of%20%20Sept-2024.pdf` | L, I |
| 2024-09 | state | NSQ | State Drug Alert for the Month of September 2024 (2024-10-24) | `MTIwODM=` (12083) | UAF`State%20NSQ%20Alert%20For%20The%20Month%20Of%20Sept-2024.pdf` | L, I |
| 2024-09 | central | spurious | List of ... declared as Spurious ... September 2024 (2024-10-24) | `MTIwODI=` (12082) | not found | L |
| 2024-10 | central | NSQ | Drug Alert for the Month of October 2024 (2024-11-29) | `MTIyMDQ=` (12204) | `https://cdsco.mohfw.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/NSQ%20ALERT%20FOR%20THE%20MONTH%20OF%20OCTOBER-2024.pdf` | L, I |
| 2024-10 | state | NSQ | State Drug Alert for the Month of October 2024 (2024-11-29) | `MTIyMDI=` (12202) | not found | L |
| 2024-10 | central | spurious | List of ... declared as Spurious ... October 2024 (2024-11-29) | `MTIyMDM=` (12203) | not found | L |
| 2024-11 | central | NSQ | Drug Alert for the Month of November 2024 (2024-12-27) | `MTIyOTI=` (12292) | not found | L |
| 2024-11 | state | NSQ | State Drug Alert for the Month of November 2024 (2024-12-27) | `MTIyOTA=` (12290) | not found | L |
| 2024-11 | central | spurious | List of ... declared as Spurious ... November 2024 (2024-12-27) | `MTIyOTE=` (12291) | not found | L |
| 2024-11 | combined | NSQ revised | Revise list drug alert November-2024 (2025-04-18) | `MTI2NzA=` (12670) | not found | L |
| 2024-12 | central | NSQ | Drug Alert for the Month of December 2024 (2025-01-24) | `MTIzOTM=` (12393) | not found | L |
| 2024-12 | state | NSQ | State Drug Alert for the Month of December 2024 (2025-01-24) | `MTIzOTQ=` (12394) | UAF`STATE%20NSQ%20ALERT%20FOR%20THE%20MONTH%20OF%20DEC-2024.%20(2).pdf` | L, I |
| 2025-01 | central | NSQ | NSQ ALERT FOR THE MONTH OF JANUARY-2025 (2025-02-28) | `MTI1NTU=` (12555) | UAF`NSQ%20ALERT%20FOR%20THE%20MONTH%20OF%20JANUARY-2025.pdf` | L, I |
| 2025-01 | state | NSQ | STATE NSQ ALERT FOR THE MONTH OF JANUARY-2025 (2025-02-28) | `MTI1NTY=` (12556) | UAF`STATE%20NSQ%20ALERT%20FOR%20THE%20MONTH%20OF%20JANUARY-2025.pdf` | L, I |
| 2025-01 | combined | NSQ revised | Revise list drug alert January-2025 (2025-04-18) | `MTI2NzE=` (12671) | not found | L |
| 2025-01 | combined | NSQ/spurious/adulterated/misbranded revised | List of ... NSQ/Spurious/... January 2025 Revised (2025-05-20) | `MTI3Mzc=` (12737) | not found | L |
| 2025-02 | central | NSQ | NSQ ALERT FOR THE MONTH OF Feb-2025 (2025-03-29) | `MTI2MTM=` (12613) | UAF`NSQ%20ALERT%20FOR%20THE%20MONTH%20OF%20Feb-2025.pdf` | L, I |
| 2025-02 | state | NSQ | STATE NSQ ALERT FOR THE MONTH OF FEBRUARY-2025 (2025-03-29) | `MTI2MTQ=` (12614) | not found | L |
| 2025-02 | central | spurious | List of ... declared as Spurious ... February-2025 (2025-03-29) | `MTI2MTI=` (12612) | not found | L |
| 2025-03 | central | NSQ | NOT OF STANDARD QUALITY (NSQ) ALERT FOR THE MONTH OF MARCH-2025 (2025-04-18) | `MTI2Njk=` (12669) | UAF`NSQ%20Alert%20For%20The%20Month%20of%20March-2025.pdf` | L, I |
| 2025-03 | state | NSQ | State NSQ Alert For The Month March-2025 (2025-04-18) | `MTI2Njg=` (12668) | not found | L |
| 2025-03 | central | spurious | List of ... declared as Spurious ... March- 2025 (2025-04-18) | `MTI2Njc=` (12667) | not found | L |
| 2025-04 | central | NSQ | Not Of Standard of Quality (NSQ) ALERT FOR THE MONTH OF April-2025 (2025-05-20) | `MTI3Mzg=` (12738) | not found | L |
| 2025-04 | state | NSQ | State NSQ Alert For The Month April-2025 (2025-05-20) | `MTI3Mzk=` (12739) | not found | L |
| 2025-04 | central | spurious | List of ... declared as Spurious ... April-2025 (2025-05-20) | `MTI3NDA=` (12740) | not found | L |
| 2025-05 | central | NSQ | NSQ ALERT FOR THE MONTH OF MAY-2025 (2025-06-20) | `MTI4NDc=` (12847) | UAF`NSQ%20ALERT%20MAY-2025.pdf` | L, **V** |
| 2025-05 | state | NSQ | STATE NSQ ALERT FOR THE MONTH OF MAY-2025 (2025-06-20) | `MTI4NDY=` (12846) | not found | L |
| 2025-05 | central | spurious | List of ... declared as Spurious ... May-2025 (2025-06-20) | `MTI4NDU=` (12845) | not found | L |
| 2025-05 | combined | NSQ revised | Revise list drug alert May-2025 (2025-07-18) | `MTI5NjA=` (12960) | UAF`Revisealert%20May-2025.pdf` | L, I |
| 2025-06 | central | NSQ | CDSCO NSQ ALERT FOR THE MONTH OF June 2025 (2025-07-18) | `MTI5Mjc=` (12927) | not found | L, **E** (JSP) |
| 2025-06 | state | NSQ | STATE NSQ ALERT FOR THE MONTH OF June 2025 (2025-07-18) | `MTI5MjY=` (12926) | UAF`STATE%20NSQ%20%20June%20-2025.pdf` | L, I |
| 2025-06 | central | spurious | List of spurious Drugs for the month of June-2025 (2025-07-18) | `MTI5NTk=` (12959) | UAF`List%20of%20spurious%20Drugs%20June-2025.pdf` | L, **V** |
| 2025-07 | n/a | n/a | no July 2025 entry on the Alerts page | n/a | not found | n/a |

**Related official items**

| Item (release date) | JSP num_id (decoded) | Note |
|---|---|---|
| Samples declared NSQ 2017-2023 (2024-09-11) | `MTE5NTU=` (11955) | Consolidated back-catalogue; underlying PDF name not found |
| Drug Alert for the Month of December 2023 (2024-01-19) | `MTA4NTE=` (10851) | |
| Drug Alert for the Month of Revised Dec 2023 (2024-02-21) | `MTA5NDA=` (10940) | |
| Drug Alert for the Month of Revised March 2023 (2024-02-21) | `MTA5NDE=` (10941) | |
| Alert on theft of multiple drug products of M/s. Novo Nordisk during transit (2025-08-21) | `MTMxNzQ=` (13174) | Theft/batch alert |
| corrigendum of (M/s. Spectra Medical Pvt Ltd) dated 21.08.2025 (2025-08-21) | `MTMzMzM=` (13333) | |
| Availability of Not Standard Quality (NSQ) Alert on New Link in CDSCO Website (2025-08-28) | `MTMyNDU=` (13245) | Fetch returned empty body (E) |

Source for all rows: [CDSCO Alerts](https://cdsco.gov.in/opencms/opencms/en/Notifications/Alerts/).

- Other UploadAlertsFiles names seen in the index (older lists): `daapril17.pdf`, `decDrug%20Alert%20List.pdf` (www host), `List%20of%20Drug%20Alert%20March2023.pdf`, `julu21DrugAlertList.pdf`. [daapril17](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/daapril17.pdf); [March 2023](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/List%20of%20Drug%20Alert%20March2023.pdf); [julu21](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadAlertsFiles/julu21DrugAlertList.pdf)
- `UploadIndustryCommon/listnsq.pdf` lists manufacturing units with more than five NSQ samples. It is firm-level, not batch-level. [listnsq.pdf](https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadIndustryCommon/listnsq.pdf)

**Table B: mirror PDFs for the legacy months (TheHealthMaster)**

All URLs are copied exactly from the index page. [TheHealthMaster index](https://thehealthmaster.com/drug-alert-nsq-drugs-lists/). Prefix `https://thehealthmaster.com/wp-content/uploads/`.

| Month | Central (CDSCO) | State | Spurious / revised |
|---|---|---|---|
| 2024-01 | `2024/02/Drug-Alert-January-2024.pdf` (single list) | none | Revised: `2024/03/Drug-Alert-January-2024-Revised.pdf` |
| 2024-02 | `2024/03/Drug-Alert-February-2024.pdf` (single) | none | none |
| 2024-03 | `2024/04/Drug-Alert-March-2024.pdf` (single) | none | none |
| 2024-04 | `2024/05/Drug-Alert-April-2024.pdf` | none | `2024/05/Spurious-Drug-Alert-April-2024.pdf` |
| 2024-05 | `2024/06/Drug-Alert-May-2024-CDSCO.pdf` | `2024/06/Drug-Alert-May-2024-States.pdf` | none |
| 2024-06 | `2024/07/Drug-Alert-June-2024-CDSCO.pdf` | `2024/07/Drug-Alert-June-2024-States.pdf` | none |
| 2024-07 | `2024/08/Drug-Alert-July-2024-CDSCO.pdf` | `2024/08/Drug-Alert-July-2024-States.pdf` | none |
| 2024-08 | `2024/09/Drug-Alert-August-2024-CDSCO.pdf` | `2024/09/Drug-Alert-August-2024-States.pdf` | `2024/11/Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-Adulterated-Misbranded-August-2024.pdf` |
| 2024-09 | `2024/10/Drug-Alert-September-2024-CDSCO.pdf` | `2024/10/Drug-Alert-September-2024-States.pdf` | `2024/11/Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-September-2024.pdf` |
| 2024-10 | `2024/11/Drug-Alert-October-2024-CDSCO.pdf` | `2024/11/Drug-Alert-October-2024-States.pdf` | `2024/11/Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-October-2024.pdf` |
| 2024-11 | `2024/12/Drug-Alert-November-2024-CDSCO.pdf` | `2024/12/Drug-Alert-November-2024-States.pdf` | `2024/12/Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-November-2024.pdf`; Revised: `2025/04/Drug-Alert-November-2024-Revised.pdf` |
| 2024-12 | `2025/01/Drug-Alert-December-2024-CDSCO.pdf` | `2024/11/Drug-Alert-December-2024-States.pdf` | none |
| 2025-01 | `2025/03/Drug-Alert-January-2025-CDSCO.pdf` | `2025/03/Drug-Alert-January-2025-States.pdf` | Revised: `2025/04/Drug-Alert-January-2025-Revised.pdf`; `2025/05/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Not-of-Standard-Quality-Spurious-Adulterated-Misbranded-for-the-Month-of-January-2025-Revised.pdf` |
| 2025-02 | `2025/03/Drug-Alert-February-2025-CDSCO.pdf` | `2025/03/Drug-Alert-February-2025-States.pdf` | `2025/03/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-February-2025.pdf` |
| 2025-03 | `2025/04/Drug-Alert-March-2025-CDSCO.pdf` | `2025/04/Drug-Alert-March-2025-States.pdf` | `2025/04/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-March-2025.pdf` |
| 2025-04 | `2025/05/Drug-Alert-April-2025-CDSCO.pdf` | `2025/05/Drug-Alert-April-2025-States.pdf` | `2025/05/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-for-the-Month-of-April-2025.pdf` |
| 2025-05 | `2025/06/Drug-Alert-May-2025-CDSCO.pdf` | `2025/06/Drug-Alert-May-2025-States.pdf` | `2025/06/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-for-the-Month-of-May-2025.pdf` |
| 2025-06 | `2025/07/Drug-Alert-June-2025-CDSCO.pdf` | `2025/07/Drug-Alert-JUne-2025-States.pdf` | `2025/07/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-for-the-Month-of-June-2025.pdf` |
| 2025-07 | `2025/08/Drug-Alert-July-2025-CDSCO.pdf` | `2025/08/Drug-Alert-July-2025-States.pdf` | none |

- Other mirrors of legacy lists:
  - Medical Dialogues `pdf_upload` copy of the Jan 2025 central list: https://medicaldialogues.in/pdf_upload/nsq-alert-for-the-month-of-january-2025-277058.pdf [MD pdf_upload](https://medicaldialogues.in/pdf_upload/nsq-alert-for-the-month-of-january-2025-277058.pdf)
  - Scribd copy of May 2025, login-walled. [Scribd](https://www.scribd.com/document/889346994/NSQ-ALERT-MAY-2025)
- Legacy-month counts reported:

| Month | Count reported | Source |
|---|---|---|
| Oct 2024 | 90 NSQ | [THM](https://thehealthmaster.com/2024/11/30/drug-alert-90-drug-samples-declared-as-nsq-in-october-2024/) |
| Feb 2025 | 103 NSQ | [THM](https://thehealthmaster.com/2025/03/29/103-drugs-as-nsq-in-february-2025/) |
| Apr 2025 | 196 NSQ (ANI story dated 20 May 2025) | [ANI](https://aninews.in/news/national/general-news/cdsco-flags-196-drugs-as-not-of-standard-quality20250520215243/) |
| May 2025 | 186 NSQ | [THM](https://thehealthmaster.com/2025/06/21/186-drug-samples-nsq-in-may-2025/) |

  Blacklisted.co.in lists batch counts per month: Jan 2024 = 46 through Dec 2024 = 135 (877 for 2024). For 2025 it lists Jan 145, Feb 103, Mar 131, Apr 196, May 188, Jun 184, Jul 143. [blacklisted.co.in index](https://blacklisted.co.in/medicines/nsq)

### Inferences
- **num_id is a base64-encoded integer.** For example `MTI5Mjc=` decodes to 12927. The IDs rise over time, so a crawler can decode them. It should not enumerate IDs it has not seen on the index page: that would mean probing the server, and unlisted IDs belong to other divisions' files.
- **The JSP probably returns an HTML wrapper.** Our empty WebFetch result and the Swa-hub note together suggest this, with the PDF loaded from UploadAlertsFiles. The ingest agent should resolve each JSP link to its UploadAlertsFiles URL once and store both.
- **Format changed over time.** Lists were single combined files for Jan to Apr 2024. Central and state lists are split from May 2024. Spurious lists are separate from Aug 2024, and also for Apr 2024. Revised lists supersede originals: Jan 2024, Nov 2024, Jan 2025 (twice) and May 2025. StripCheck needs a `supersedes` link and should not double-count revised rows.
- **TheHealthMaster gives near-complete coverage** for every month from Jan 2024 to Jul 2025. It is the practical fallback when a CDSCO link fails, but its files are not byte-identical to CDSCO's. Its Aug 2025 file was re-processed with Ghostscript `/ebook` settings (see Q3).

### Gaps
- I did not find direct UploadAlertsFiles names for about two-thirds of the lists (marked "not found"). Resolving them needs the JSP target, which another investigator can capture in a browser.
- The official text of the 28 Aug 2025 "New Link" notice (num_id 13245) could not be read, because the fetch returned an empty body.
- July 2025: no entry appears on the CDSCO Alerts page, yet mirror PDFs exist (THM `2025/08/...July-2025...`). I could not confirm whether CDSCO published July 2025 as a PDF elsewhere or as the first month on the portal.
- No December 2024 spurious list is listed on the official page or the mirror.
- The underlying file name of the consolidated "Samples declared NSQ 2017-2023" list was not found.
- Text extraction is unconfirmed:
  - WebFetch saw only compressed streams in the May 2025 and June 2025 spurious PDFs.
  - WebFetch cached those PDF bytes automatically in the session tool-results folder. I did not choose to download them.
  - The local PDF reader then refused all three cached PDFs (two CDSCO, one mirror) with "PDF is password-protected".
  - So the files may be encrypted, possibly with an owner/permissions password. I could not verify which.
- Row counts and column headers of the legacy PDFs could not be read through these tools.

---

## Q2. The NSQ portal used since 28 Aug 2025: HTML, scripts, endpoints, files

### Takeaway
From August 2025, CDSCO publishes NSQ and spurious lists as an online table, not as PDFs. The cdsco.gov.in page `/en/Notifications/nsq-drugs/` is an empty shell titled "NSQ Alerts". The data lives on `cdscoonline.gov.in`: a viewer at `/CDSCO/viewPublicNSQDrug` with Year, Month and Reporting Source filters and "NSQ Drugs" / "Spurious Drugs" tabs, and an unauthenticated JSON endpoint at `/CDSCO/publicNsqDrugTable`. That endpoint returned 330 SEP-2026 records in DataTables legacy format. No export or download files exist on the portal. The parameters for selecting other months were not visible to me.

### Cited Findings
- **cdsco.gov.in shell page.** https://cdsco.gov.in/opencms/opencms/en/Notifications/nsq-drugs/ shows only the title "NSQ Alerts", the organisation name and navigation links. WebFetch found no script URLs, forms, tables or PDF/XLS/CSV links in the converted page. The only "export" paths are logo images under `/opencms/export/sites/CDSCO_WEB/Image_folder/logo/`. [CDSCO nsq-drugs](https://cdsco.gov.in/opencms/opencms/en/Notifications/nsq-drugs/)
- **Viewer app.** https://cdscoonline.gov.in/CDSCO/viewPublicNSQDrug has:
  - Heading "NSQ Alerts" and tab labels "NSQ Drugs" and "Spurious Drugs".
  - Filters "Select Year", "Select Month" and "Reporting Source", with buttons "Apply Filter" and "✕ Clear All".
  - A modal "Pending States (SEP-2026)".
  - A definition of spurious drugs citing Section 17-B of the Drugs and Cosmetics Act, 1940.
  - No table rows, export buttons or script URLs in the static content WebFetch returned. [viewPublicNSQDrug](https://cdscoonline.gov.in/CDSCO/viewPublicNSQDrug)
- **JSON endpoint.** https://cdscoonline.gov.in/CDSCO/publicNsqDrugTable returns JSON.
  - Top-level keys: `iTotalRecords`, `iTotalDisplayRecords`, `aaData` (DataTables legacy server-side format).
  - Record fields: `str_product_name`, `str_batch_no`, `dt_manufacturing_date`, `dt_expiry_date`, `str_manufactured_by`, `str_nsq_result`, `str_reporting_source`, `str_reported_by_lab_or_state`, `dt_reporting_month_year`, `str_brand_name`.
  - On 25 Oct 2026 it reported 330 records, every visible one with `dt_reporting_month_year` = SEP-2026. The response was 175,849 characters.
  - Example first record: Alprazolam Tablets IP 0.5 mg, batch 60098, brand Alzomac-0.5, Mfg Feb-2026, Exp Jan-2028, Uniza Lifecare Pvt. Ltd., Gujarat, reported by a state lab in Lucknow, UP, result "does not conform to IP in respect of Dissolution".
  - Some `str_nsq_result` texts end "hence Spurious" or "Hence Misbranded".
  - Some rows (Mounjaro KwikPen) have null manufacturing and expiry dates. [publicNsqDrugTable](https://cdscoonline.gov.in/CDSCO/publicNsqDrugTable)
- **Default month changes.** A search-engine snippet of the same endpoint showed AUG-2026 records at index time. [search result for publicNsqDrugTable](https://cdscoonline.gov.in/CDSCO/publicNsqDrugTable)
- **Older SUGAM page.** https://www.cdscoonline.gov.in/CDSCO/GetNSQDrugs is a SUGAM "Consumer Information" page headed "Not of Standard Quality (NSQ) Drugs". It has Month/Year and From/To date filters plus Submit, and shows "No data Found". It has no export links and no visible AJAX endpoint. [GetNSQDrugs](https://www.cdscoonline.gov.in/CDSCO/GetNSQDrugs)
- **Community reports on the endpoint:**
  - One repo describes `cdscoonline.gov.in/CDSCO/publicNsqDrugTable` as "a plain, unauthenticated GET". It needs only `str_product_name` and ideally `str_nsq_result`, and saves `data/publicNsqDrugTable.json`. [shayadmeri-svg/nsq](https://github.com/shayadmeri-svg/nsq)
  - Another says the viewer's "data address isn't documented, so you capture it once per month" with the DevTools Network tab (Fetch/XHR) or a HAR export. [Swa-hub/nsq-medicine-tracker](https://github.com/Swa-hub/nsq-medicine-tracker)
- **Column match with Medical Dialogues.** For Sep 2026, Medical Dialogues printed the central-lab list as an HTML table with columns "S.No, Name of Product, Batch No, Manufacturing Date, Expiry Date, Manufactured By, NSQ Result, Reporting Source, Reporting by Lab/State, Reporting Month & Year". The product cell embeds "(Brand Name : NA)", and Reporting Source is "CDSCO Labs". [MD Sep 2026](https://medicaldialogues.in/news/industry/pharma/nsq-alert-42-drug-surgical-product-samples-fail-cdsco-quality-tests-in-september-181886)

### Inferences
- The `publicNsqDrugTable` endpoint is the authoritative machine-readable source for Aug 2025 onward. With no parameters it serves the latest month (SEP-2026 on 25 Oct 2026).
- The 10 JSON fields correspond to the 10 columns in the Medical Dialogues table. The portal UI appears to merge `str_brand_name` into the product cell. StripCheck's product and brand corroboration can use both fields.
- The "Pending States (SEP-2026)" modal implies that some states had not yet reported when the month was published. A month's row count can therefore change after first release. StripCheck should snapshot the JSON with a fetch timestamp and re-poll a month later.
- Spurious records appear both in a separate "Spurious Drugs" tab and inside NSQ rows whose result text says "hence Spurious" or "Misbranded". The ingest classifier should read the result text and not rely on the tab alone.

### Gaps
- I could not see the request parameters (year, month, reporting source; DataTables `sEcho`/`iDisplayStart`/`iDisplayLength`) or the endpoint behind the "Spurious Drugs" tab. WebFetch converts pages to markdown and strips scripts. This is left to the browser investigator. I did not guess any parameter names.

### Browser investigation (coordinator, 25 Oct 2026): gap closed
Read from the viewer page's own JavaScript in the built-in browser, then called from a plain shell with no cookies.
- **Wiring.** `cdsco.gov.in/.../nsq-drugs/` embeds an iframe whose `src` is `https://cdscoonline.gov.in/CDSCO/viewPublicNSQDrug`.
- **Endpoints** (all plain unauthenticated GETs; TLS verifies; no session cookie needed):

  | Purpose | Request | Returns |
  |---|---|---|
  | Years available | `/CDSCO/reportingYears?tab=nsq` (or `tab=spurious`) | `["2019",...,"2026"]` for nsq; `["2025","2026"]` for spurious |
  | Months in a year | `/CDSCO/publicReportingMonths?year=2025&tab=nsq` | `["Jan",...,"Dec"]`; the UI builds the month key as `<Mon>-<YYYY>` |
  | NSQ rows for a month | `/CDSCO/filteredNsqDrugTable?month=AUG-2025&source=All&tab=nsq` (`source` = `All`, `State` or `CDL`) | `{"aaData":[...]}` |
  | Spurious rows for a month | `/CDSCO/filteredSpuriousDrugTable?month=SEP-2026&source=All&tab=spurious` | `{"aaData":[...]}` |
  | Latest NSQ month (default view) | `/CDSCO/publicNsqDrugTable` | latest month only (SEP-2026: 330 rows) |
  | Latest spurious (default view) | `/CDSCO/viewPublicSpuriousDrugData` | latest month only |
- **Encoding.** Responses are `Content-Type: text/plain;charset=ISO-8859-1`, not UTF-8 (a `0xA9` byte broke a UTF-8 decode). Decode as latin-1.
- **NSQ fields:** `str_product_name, str_brand_name, str_batch_no, dt_manufacturing_date, dt_expiry_date, str_manufactured_by, str_nsq_result, str_reporting_source, str_reported_by_lab_or_state, dt_reporting_month_year`.
- **Spurious fields** (richer): `product_name_from_dtl, str_brand_name, str_dosage_form, str_route, str_nsq_category, str_manufacturer_name, str_manufactured_by, str_manufacturing_state, dt_manufacturing_date, dt_expiry_date, str_batch_no, str_nsq_result, num_spurious_flag, str_spurious_manufacturer_name, str_spurious_manufactured_by, dt_spurious_date, str_nsq_remarks, str_firm_reply, str_reporting_source, str_reported_by_lab_or_state, dt_reporting_month_year, num_id`. Example: `str_firm_reply` = "The actual manufacturer (as per label claim) has informed that the impugned batch of the product has not been manufactured by them and that it is a spurious drug."
- **Coverage.** A polite snapshot (one request every 1.5 s, 108 files, 3.7 MB, no failures) returned NSQ data for every month from JAN-2019 to SEP-2026 (93 months) and spurious-tab data for 2025-2026. Rows per month seen in the log include AUG-2025 94, OCT-2025 211, NOV-2025 216, DEC-2025 175, JAN-2026 218, FEB-2026 217, MAR-2026 190, APR-2026 121, MAY-2026 162, JUN-2026 193, JUL-2026 239, AUG-2026 220, SEP-2026 330. These match the Blacklisted counts in Table C exactly, which suggests Blacklisted exports this same feed.
- **Data-quality notes seen in the feed:** reporting-source spellings vary ("CDSCO lab", "CDSCO Labs", "State Lab", "State lab"); lab names vary ("CDL Kolkata" vs "CDL, Kolkata"); brand is "NA" in older months and separate from the product name in newer ones (older months embed the brand in brackets in the product name); placeholder makers such as "NIL,NIL NIL"; odd batch strings such as "Up -to -01", "CBC-0012/25" and very short ones such as "155"; some rows have null dates (e.g., Mounjaro KwikPen).
- **Snapshot statistics (25 Oct 2026; exploratory script, to be regenerated from the DB by `cli.py stats`):**
  - 7,005 rows: 6,956 from the NSQ tab over 93 months (2019-01 to 2026-09) + 49 from the spurious tab (2025-06 to 2026-09). Rows per month: min 8, median 48, max 330.
  - NSQ rows by year: 2019 404 · 2020 326 · 2021 345 · 2022 572 · 2023 644 · 2024 877 · 2025 1,898 · 2026 (Jan-Sep) 1,890.
  - Reporting source: state labs 3,822, CDSCO labs 3,178. Brand field present in only 13.8% of NSQ rows (newer months); older rows embed the brand in brackets in the product name.
  - 121 rows mention "spurious" across both tabs.
  - Batch keys: 6,667 distinct; length mostly 6-9; 2.4% shorter than 4 characters; 268 keys appear more than once (148 same product re-listed, 36 shared by unrelated products, e.g. `8S17004` for three different medicines).
  - Confusable neighbours: 95 keys (1.42%) have another listed key one OCR-confusable substitution away; 58 (0.87%) of those share the maker, e.g. `R21119`/`R21719` (both ciprofloxacin), `BPT6611`/`BPT6617`, `TACB011`/`TACB017`, `S2FBV33`/`S2FBV38`. Sequential batch numbering creates such siblings, and since only sampled batches are listed, unlisted siblings of listed batches must be common in the market.
  - Alert lag (reporting month minus manufacturing month): median 10 months, IQR 6-15, p90 20.
  - Remaining shelf life at alert (expiry minus reporting month): median 14 months, IQR 9-18; 63.5% have at least 12 months left; 0.58% already expired. Flagged batches are still in circulation when the alert appears.
  - Data errors: 1.6% missing dates; 14 rows with manufacturing after expiry; 16 rows with manufacturing after the reporting month.
  - Failure categories (multi-label): assay/content 2,925 · dissolution 1,903 · description 952 · particulate matter 412 · labelling/misbranded 364 · identification 362 · pH 298 · sterility 291 · disintegration 266 · uniformity 235.
  - Cleaning rules needed: split multi-batch cells (`PFB-701, OPCP-195`), strip trailing commas and GS1 prefixes (`(10)CITW-31`), treat `?` as a lost dash (latin-1 replacement), normalise lab-name variants (`CDL Kolkata` / `CDL, Kolkata`), flag batch cells that are words (`Up -to -01`). The feed also contains cosmetics and medical devices (shampoo, syringes).
- **Implication for StripCheck.** The portal JSON should be the primary ingest source for 2019-2026 (one adapter, upsert by natural key, re-poll the latest 2-3 months because of "Pending States"), with legacy PDFs kept as a secondary source for page-level provenance crops and for an automatic PDF-parsing accuracy check against the JSON on overlapping months.
- How cdsco.gov.in's nsq-drugs page connects to cdscoonline.gov.in (iframe, redirect or link) is not confirmed.
- No CDSCO documentation, API terms or rate limits for the endpoint were found.

---

## Q3. Press and third-party mirrors, Aug 2025 to Oct 2026: full-list URLs and reported counts

### Takeaway
The most recent published month is **September 2026**: 330 NSQ (42 central + 288 state) and 1 spurious (Delhi), reported 23 Oct 2026 and matching the portal JSON's `iTotalRecords` of 330. **No October 2026 list exists yet.** For every month from Aug 2025 to Aug 2026, TheHealthMaster hosts PDFs (central, state and usually spurious). Medical Dialogues prints full HTML tables of the central and state lists. Blacklisted.co.in offers per-month HTML pages and a CSV. Press totals often disagree with each other and with third-party row counts.

### Cited Findings

**Table C: monthly counts reported, Aug 2025 to Oct 2026**

| Report month | Total NSQ (central + state) | Spurious | Count sources | Conflicts / notes |
|---|---|---|---|---|
| Aug 2025 | 94 (34 + 60) | 3 (Bihar) | [Pharmabiz](https://www.pharmabiz.com/PrintArticle.aspx?aid=181362&sid=1); [Business Standard](https://www.business-standard.com/industry/news/cdsco-spurious-drugs-nsq-august-2025-125091900835_1.html) | Blacklisted 94 |
| Sep 2025 | 112 (central/state split unconfirmed; "52 CDSCO" seen only in a roundup snippet) | not found | [Outlook India](https://www.outlookindia.com/healthcare-spotlight/112-drug-samples-declared-not-of-standard-quality-in-september-cdsco) | Blacklisted 112 |
| Oct 2025 | 211 (63 + 148) | 5 (3 Bihar + 2 Delhi) | [Social News XYZ, 21 Nov 2025](https://www.socialnews.xyz/2025/11/21/cdsco-labs-flag-211-drug-samples-as-not-of-standard-quality-in-october/) | Blacklisted 211 |
| Nov 2025 | 205 (64 + 141) | not found | [THM](https://thehealthmaster.com/2025/12/25/drug-alert-205-samples-declared-nsq-november-2025/); [Sentinel Assam](https://www.sentinelassam.com/topheadlines/cdsco-labs-flag-205-drugs-as-not-of-standard-quality); [MD central 64](https://medicaldialogues.in/news/industry/pharma/cdsco/cdsco-alert-64-drug-batches-including-metformin-paracetamol-declared-not-of-standard-quality-in-november-161064) | Blacklisted 216 |
| Dec 2025 | 167 | 7 | [NewsGram](https://www.newsgram.com/health/2026/01/22/cdsco-flags-167-drug-samples); [THM](https://thehealthmaster.com/2026/01/31/drug-alert-167-drug-samples-declared-as-nsq-in-december-2025/) | Blacklisted 175 |
| Jan 2026 | Conflicting: 214 (ETV Bharat Q1 total); 240 = 68 + 172 (Pharma Industrial India); MD 68 central + 147 state | 3 (Delhi, Uttarakhand, West Bengal) per PII | [Pharma Industrial India](https://www.pharmaindustrial-india.com/news/cdsco-flags-240-drug-samples-as-not-of-standard-quality-in-january-2026); [ETV Bharat](https://www.etvbharat.com/en/health/cdsco-detects-168-not-of-standard-quality-and-spurious-medicines-in-march-enn26042103333); [MD central](https://medicaldialogues.in/news/industry/pharma/cdsco-flags-68-drug-batches-including-albendazole-meropenem-as-not-of-standard-quality-in-january-165248); [MD state](https://medicaldialogues.in/amp/news/industry/pharma/state-drug-alert-147-medicine-samples-fail-cdsco-quality-tests-in-january-2026-165395) | Blacklisted 218 |
| Feb 2026 | 194 (60 + 134) | 4 | [Business Standard](https://www.business-standard.com/industry/news/cdsco-flags-4-spurious-drugs-194-fail-quality-tests-feb-2026-126032301221_1.html); [BioPatrika](https://biopatrika.com/industry/regulatory/cdsco-flags-spurious-drugs-and-substandard-medicines/); [MD central 60](https://medicaldialogues.in/news/industry/pharma/cdsco/nsq-drug-alert-60-batches-including-paracetamol-cefixime-telmisartan-fail-cdsco-quality-tests-in-february-167138); [MD state 134](https://medicaldialogues.in/news/industry/pharma/cdsco/state-drug-alert-from-antibiotics-to-antihypertensives-134-samples-found-nsq-in-february-audit-167283) | Blacklisted 217 |
| Mar 2026 | 168 | 1 (Bihar) | [Pharmabiz](https://www.pharmabiz.com/PrintArticle.aspx?aid=185491&sid=2); [ETV Bharat](https://www.etvbharat.com/en/health/cdsco-detects-168-not-of-standard-quality-and-spurious-medicines-in-march-enn26042103333); [MD central 48](https://medicaldialogues.in/news/industry/pharma/cdsco/48-drug-batches-fail-quality-tests-in-cdscos-march-2026-nsq-alert-169303) | Blacklisted 190 |
| Apr 2026 | 169 (42 + 127 per Pharmabiz; the420 gives 42 + 129, which sums to 171) | 1 (Bihar; ursodeoxycholic acid per the420) | [Pharmabiz](https://www.pharmabiz.com/NewsDetails.aspx?aid=186069&sid=2); [the420](https://the420.in/cdsco-april-drug-quality-tests-spurious-medicine-patient-safety/); [MD state 78 (NSQ + spurious + misbranded)](https://medicaldialogues.in/news/industry/pharma/cdsco/state-drug-alert-cdsco-flags-78-nsq-spurious-misbranded-drug-samples-in-april-quality-checks-171331) | Blacklisted 121 |
| May 2026 | 157 (PharmaTutor; MD 46 + 111) or 159 (46 + 113, Daily Pioneer; DrugsControl.org) | 2 (PharmaTutor) or 1 (Assam: ANI, DrugsControl.org) | [PharmaTutor](https://www.pharmatutor.org/pharma-news/2026/cdsco-flags-157-drug-samples-as-not-of-standard-quality-2-declared-spurious-in-may-2026); [Daily Pioneer](https://dailypioneer.com/news/slug-lite/cdsco-finds-46-drug-samples-not-of-standard-quality-for-may?year=2026); [DrugsControl.org](https://drugscontrol.org/news-detail.php?newsid=45230); [ANI](https://aninews.in/news/national/general-news/one-spurious-drug-sample-from-assam-detected-in-may-2026-probe-underway-cdsco-report20260624160517/); [MD central 46](https://medicaldialogues.in/news/industry/pharma/cdsco-flags-46-drug-batches-including-thyroxine-amoxycillin-clavulanate-as-nsq-in-may-2026-173615); [MD state 111](https://medicaldialogues.in/news/industry/pharma/state-drug-alert-111-batches-including-paracetamol-telmisartan-fail-cdsco-quality-tests-173683) | Blacklisted 162 |
| Jun 2026 | 159 | not found | [THM](https://thehealthmaster.com/2026/07/22/drug-alert-159-drug-samples-declared-as-nsq-in-june-2026/); [MD central 27 (month per search summary, unverified)](https://medicaldialogues.in/news/industry/pharma/cdsco/cdsco-flags-27-drug-batches-including-paracetamol-ibuprofen-levetiracetam-as-not-of-standard-quality-175531) | Blacklisted 193 |
| Jul 2026 | 280 (40 + 240) per ETV Bharat and Pharmabiz, vs 239 (40 + 199) per THM and Blacklisted ("CDSCO NSQ portal export (239 rows)") | 1 (Bihar); Blacklisted lists Buprenorphine Inj. batch LM1888 (CDL Kolkata) | [ETV Bharat](https://www.etvbharat.com/en/bharat/cdsco-flags-280-drug-samples-as-nsq-or-spurious-in-july-enn26082107816); [THM](https://thehealthmaster.com/2026/09/01/drug-alert-239-drug-samples-declared-as-nsq-in-july-2026/); [Blacklisted 2026-07](https://blacklisted.co.in/medicines/nsq/2026-07) | [Nagaland Post](https://nagalandpost.com/40-samples-found-not-of-standard-quality-by-central-drugs-laboratories/) labels the 40/240 figures as August, which conflicts |
| Aug 2026 | 220 (29 + 191) | Delhi (count not stated in headline) | [Pharmabiz](https://www.pharmabiz.com/PrintArticle.aspx?aid=190752&sid=2); [The News Mill](https://thenewsmill.com/2026/09/cdsco-flags-220-drug-samples-as-nsq-in-august-spurious-drug-in-delhi/); [THM](https://thehealthmaster.com/2026/09/23/drug-alert-220-drug-samples-declared-as-nsq-in-august-2026/); [MD central 29](https://medicaldialogues.in/news/industry/pharma/29-drug-batches-including-haloperidol-amikacin-rabeprazole-fail-cdsco-quality-tests-179785) | Blacklisted 220 |
| Sep 2026 | 330 (42 + 288) | 1 (Delhi) | [ANI, 23 Oct 2026](https://aninews.in/news/national/general-news/cdsco-flags-330-substandard-drug-samples-one-spurious-medicine-in-september-surveillance20261023114826/); [The News Mill](https://thenewsmill.com/2026/10/cdsco-identifies-330-substandard-drugs-and-one-spurious-medicine-in-september-testing/); [MD central 42](https://medicaldialogues.in/news/industry/pharma/nsq-alert-42-drug-surgical-product-samples-fail-cdsco-quality-tests-in-september-181886); [portal JSON 330](https://cdscoonline.gov.in/CDSCO/publicNsqDrugTable) | MD central breakdown: CDL Kolkata 31, RDTL Guwahati 5, RDTL Chandigarh 4, CDTL Mumbai 1, CDTL Hyderabad 1 |
| Oct 2026 | not yet published (as of 25 Oct 2026) | n/a | The portal default month is SEP-2026, with a "Pending States (SEP-2026)" modal ([viewer](https://cdscoonline.gov.in/CDSCO/viewPublicNSQDrug)) | see Inferences |

**Table D: full-list mirrors, Aug 2025 to Aug 2026 (TheHealthMaster PDFs)**

All URLs are exact from the index page. [THM index](https://thehealthmaster.com/drug-alert-nsq-drugs-lists/). Prefix `https://thehealthmaster.com/wp-content/uploads/`.

| Month | Central (CDSCO) PDF | State PDF | Spurious PDF |
|---|---|---|---|
| 2025-08 | `2025/09/Drug-Alert-August-2025-CDSCO.pdf` (**V**: 206.5 KB, 11 pages, Ghostscript `/ebook` re-processed) | `2025/09/Drug-Alert-August-2025-States.pdf` | none |
| 2025-09 | `2025/10/Drug-Alert-September-2025-CDSCO.pdf` | `2025/10/Drug-Alert-September-2025-States.pdf` | `2025/10/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-drug-September-2025.pdf` |
| 2025-10 | `2025/11/Drug-Alert-October-2025-CDSCO.pdf` | `2025/11/Drug-Alert-October-2025-States.pdf` | `2025/11/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-drug-October-2025.pdf` |
| 2025-11 | `2025/12/Drug-Alert-November-2025-CDSCO.pdf` | `2025/12/Drug-Alert-November-2025-States.pdf` | `2025/12/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-drug-November-2025.pdf` |
| 2025-12 | `2026/01/Drug-Alert-December-2025-CDSCO.pdf` | `2026/01/Drug-Alert-December-2025-States.pdf` | `2026/01/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-drug-December-2025.pdf` |
| 2026-01 | `2026/02/Drug-Alert-january-2026-CDSCO.pdf` | `2024/11/Drug-Alert-January-2026-States.pdf` | `2026/02/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-drug-January-2026.pdf` |
| 2026-02 | `2026/03/Drug-Alert-February-2026-CDSCO.pdf` | `2026/03/Drug-Alert-February-2026-States.pdf` | `2026/03/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-drug-February2026.pdf` |
| 2026-03 | `2026/04/Drug-Alert-March-2026-CDSCO.pdf` | `2026/04/Drug-Alert-March-2026-States.pdf` | `2026/04/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-drug-March-2026.pdf` |
| 2026-04 | **missing**: the "CDSCO" link points to the States file | `2026/05/Drug-Alert-April-2026-States.pdf` | `2026/05/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-drug-April-2026.pdf` |
| 2026-05 | `2026/06/Drug-Alert-May-2026-CDSCO.pdf` | `2026/06/Drug-Alert-May-2026-States.pdf` | `2026/07/Drug-Alert-May-2026-Spurious-Drugs.pdf` |
| 2026-06 | `2026/07/Drug-Alert-June-2026-CDSCO.pdf` | `2026/07/Drug-Alert-June-2026-States.pdf` | none |
| 2026-07 | `2024/11/Drug-Alert-July-2026-CDSCO.pdf` | `2024/11/Drug-Alert-July-2026-States.pdf` | `2026/08/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-drug-July-2026.pdf` |
| 2026-08 | `2026/09/Drug-Alert-August-2026-CDSCO.pdf` | `2026/09/Drug-Alert-August-2026-States.pdf` | `2026/09/List-of-Drugs-Medical-Devices-Vaccine-and-Cosmetics-declared-as-Spurious-drug-August-2026.pdf` |
| 2026-09 | not on THM index yet | not on THM index yet | not on THM index yet |

**Other mirrors**
- **Medical Dialogues** prints full HTML tables. The Sep 2026 central list has 42 rows in 10 columns (verified). Monthly central/state article URLs are in Table C. No PDF or `pdf_upload` link appears in the Sep 2026 article. [MD Sep 2026](https://medicaldialogues.in/news/industry/pharma/nsq-alert-42-drug-surgical-product-samples-fail-cdsco-quality-tests-in-september-181886)
- **Blacklisted.co.in**:
  - Per-month HTML pages at `https://blacklisted.co.in/medicines/nsq/YYYY-MM`. The index covers 92 months, Jan 2019 to Aug 2026, with no Sep 2026 page at fetch time.
  - Per-month CSV at `/data/nsq/2026-07.csv`, an all-months CSV at `/data/nsq/all.csv`, and an RSS feed at `/medicines/nsq/feed.xml`.
  - Page fields: product, batch with Mfg/Exp, manufacturer and state, NSQ reason (text and category), testing lab (State or CDSCO), and a separate "suspected spurious" section.
  - Terms: "Free to reuse with credit"; "Source documents belong to their publishers".
  - Counts for Aug 2025 to Aug 2026: 94, 112, 211, 216, 175, 218, 217, 190, 121, 162, 193, 239, 220. [Blacklisted index](https://blacklisted.co.in/medicines/nsq); [Blacklisted Jul 2026](https://blacklisted.co.in/medicines/nsq/2026-07)
- **FirstScanIt** "CDSCO Drug Alerts" is only a launcher. It holds no records, exports or licence, and points users to cdsco.gov.in. [FirstScanIt](https://firstscanit.com/tools/cdsco-failed-drugs)
- **Legality Simplified** summarises monthly lists, for example Feb 2025, June 2025 and the Nov 2024 / Jan 2025 revisions. [Legality Simplified Jun 2025](https://www.legalitysimplified.com/cdsco-publishes-not-of-standard-quality-and-spurious-alert-for-june-2025/); [revisions](https://www.legalitysimplified.com/cdsco-revises-drug-alert-list-for-november-2024-january-2025/)
- **Press wording.** Coverage repeats that CDSCO displays the NSQ and spurious list on its portal monthly, and that a failure applies only to the batch tested. [ANI Sep 2026](https://aninews.in/news/national/general-news/cdsco-flags-330-substandard-drug-samples-one-spurious-medicine-in-september-surveillance20261023114826/)
- **No PIB release found.** No pib.gov.in release for the monthly lists surfaced in search. Coverage relays CDSCO / health-ministry statements. [search: ANI / Pharmabiz results](https://aninews.in/news/national/general-news/one-spurious-drug-sample-from-assam-detected-in-may-2026-probe-underway-cdsco-report20260624160517/)

### Inferences
- **Release cadence.** Dates embedded in article URLs suggest the portal-era lists appear around the 19th to 24th of the following month:

  | List month | Published (URL date) |
  |---|---|
  | Aug 2025 | 19 Sep 2025 (Business Standard) |
  | Feb 2026 | 23 Mar 2026 |
  | Mar 2026 | 21 Apr 2026 |
  | May 2026 | 24 Jun 2026 |
  | Jul 2026 | 21 Aug 2026 |
  | Sep 2026 | 23 Oct 2026 |

  Legacy PDFs were released on the 17th to 29th. The **October 2026 list should appear around 18 to 25 Nov 2026**. This is an estimate, not an official schedule. The medicine-cabinet re-check job can poll daily from the 15th to the 30th of each month.
- **Counts disagree across sources.** Third-party row counts (Blacklisted) and press totals differ by up to about 50 rows in several months (Apr 2026: 121 vs 169; Jun 2026: 193 vs 159; Jul 2026: 239 vs 280). Possible reasons include spurious and misbranded rows, revisions, late state data, and cosmetics or devices. StripCheck should treat its own ingested JSON row count as ground truth for its index, and log the press figure only as a reconciliation check.
- **Origin of THM PDFs for portal months is unclear.** For Aug 2025 onward, CDSCO published no PDFs, so the TheHealthMaster files are either CDSCO-supplied PDFs or prints of the portal. They are usable for back-filling months the JSON endpoint cannot serve without parameters, but should be marked as secondary provenance.

### Gaps
- I could not verify per-month row counts from the portal for any month except Sep 2026 (330), because of the parameter gap in Q2.
- Spurious counts are missing for Sep 2025, Nov 2025 and Jun 2026. The Aug 2026 spurious count is not explicit.
- The month attribution of the MD "27 batches" article (assumed Jun 2026) and the Jan 2026 totals are unresolved.
- The origin of TheHealthMaster's post-Aug 2025 PDFs (CDSCO-supplied or portal print) is unknown.
- The Medical Dialogues state-list article URLs for Aug and Sep 2026 were not located.

---

## Q4. State drug-controller sources that publish NSQ / spurious batch lists

### Takeaway
Only a few states publish usable batch-level lists online:
- **Maharashtra FDA:** one HTML table of 197 rows, updated 16 Oct 2026.
- **Kerala Drugs Control Department:** monthly "Not of Standard Quality Drugs for the month ..." posts, but its TLS certificate had expired on 25 Oct 2026.
- **Tamil Nadu:** a "List of NSQ Drugs" page with April to August 2026 entries in the search cache; the TLS chain failed verification.

Karnataka's regulator site shows only a 2023 circular. Telangana pushes NSQ alerts by bulk SMS and issues ad-hoc stop-use notices, with no web list found. No Himachal Pradesh regulator list was found. Most state-lab results reach CDSCO's monthly state list anyway.

### Cited Findings

**Table E: state sources**

| State | URL | Format | Update frequency / status (25 Oct 2026) | Source |
|---|---|---|---|---|
| Maharashtra (FDA) | https://fda.maharashtra.gov.in/nsq-alerts/ | Single HTML table, 197 rows. Columns: "Sr. No.", "Name of Product/ Drug", "Manufactured by", "Batch No.", "Mfg. Date", "Exp. Date", "Reason for NSQ". Includes cosmetics. No lab or month column, no PDF/XLS, no pagination. | "Last Updated: 16.10.2026". Mfg dates range from Mar 2024 to Jul 2026. Some rows say "NOT MENTIONED" or have inconsistent dates. | [Maharashtra FDA NSQ](https://fda.maharashtra.gov.in/nsq-alerts/) |
| Kerala (Drugs Control Dept.) | https://dc.kerala.gov.in/en/category/substandard-drugs/ | Monthly category posts "Not of Standard Quality Drugs for the month …" (attachment format not confirmed) | The search cache shows entries from 2021, latest visible "JANUARY 2026". WebFetch failed with "certificate has expired". | [Kerala DCD](https://dc.kerala.gov.in/en/category/substandard-drugs/) |
| Kerala (press) | UNI, 3 Oct 2026: Kerala banned 41 batches found NSQ in September 2026 tests. Earlier: 14 batches (Oct 2025 tests); 17 medicines. | News text | Monthly bans continue. | [UNI](https://www.uniindia.com/south-india/health-kerala-drugs-ban-03ms28/201775); [South First](https://thesouthfirst.com/kerala/kerala-bans-17-substandard-medicines-in-major-crackdown-on-unsafe-drugs/) |
| Kerala (aggregator) | https://drugsip.blogspot.com/p/nsq-drugs.html | Blog compilation of Kerala monthly lists | Not verified | [drugsip blog](https://drugsip.blogspot.com/p/nsq-drugs.html) |
| Tamil Nadu (Food Safety & Drugs Admin.) | https://www.drugscontrol.tn.gov.in/list_nsq_drugs.html | "List of NSQ Drugs" page; per the search snippet it reposts CDSCO monthly lists | Search cache shows Apr to Aug 2026 entries. WebFetch failed with "unable to verify the first certificate". | [TN NSQ list](https://www.drugscontrol.tn.gov.in/list_nsq_drugs.html); [TN home](https://drugscontrol.tn.gov.in/) |
| Karnataka (Drugs Control Dept.) | https://drugs.karnataka.gov.in/en | "List of NSQ Drugs" circular dated 2023-05-08 under Circulars/Notifications | No current monthly list found | [Karnataka DCD](https://drugs.karnataka.gov.in/en) |
| Karnataka (State Pharmacy Council, not the regulator) | https://kspcdic.com/ | "NSQ Listing" with Oct 2026 alerts (per search snippet) | Not verified | [KSPC DIC](https://kspcdic.com/) |
| Telangana (DCA) | No web list found on dca.telangana.gov.in | Bulk SMS alerts to medical shops and wholesalers when the state lab declares NSQ (about 48,000 stakeholders; batch number included; WhatsApp planned). Ad-hoc public "stop use" notices, e.g. Almont-Kid syrup batch AL-24002 (ethylene glycol). | Event-driven | [Telangana Today](https://telanganatoday.com/telangana-dca-launches-bulk-drug-sms-system-alert-to-alert-medical-shops-about-substandard-drugs); [MD](https://medicaldialogues.in/news/industry/pharma/telangana-dca-introduces-sms-alert-system-to-warn-pharmacies-about-substandard-medicines-166301); [X post](https://x.com/DCATelangana/status/2030953905455263832); [Medstown](https://www.medstown.com/telangana-dca-issues-stop-use-notice-for-almont-kid-syrup-batch-al-24002-found-toxic/) |
| Himachal Pradesh | No state regulator list page found | Press coverage only (Tribune), e.g. Baddi / BBN firms in CDSCO lists | n/a | [Tribune](https://www.tribuneindia.com/news/himachal/himachal-spurious-injection-among-31-failed-drug-samples/) |

- **Maharashtra quarterly figures.** In one quarter, Maharashtra FDA declared 108 drug samples non-standard: 93 NSQ, 8 spurious and 7 misbranded. [The Week](https://www.theweek.in/news/health/2026/09/03/maharashtra-fda-steps-up-testing-over-37600-food-drug-samples-collected-in-three-months-15268-found-non-standard.html)
- **Nazar uses state feeds.** The open-source Nazar project ingests "CDSCO (online NSQ portal and alert PDFs), Tamil Nadu, Maharashtra and WHO", reports "1,404 alerts from 21 notices", and was live on 18 Oct 2026 under the MIT licence. [Nazar](https://github.com/pranshurastogi/Nazar)
- **State gaps in CDSCO lists.** Some states, such as Tamil Nadu for Feb 2025, did not submit data in the required format for a given month. [MD state alert coverage](https://medicaldialogues.in/news/industry/pharma/56-formulations-declared-not-of-standard-quality-as-per-data-provided-by-states-cdsco-drug-alert-146149)

### Inferences
- Maharashtra's table is the only state source confirmed to be machine-friendly. It has no reporting-month column, so StripCheck should stamp rows with the scrape date and de-duplicate them against CDSCO rows on (batch, product, manufacturer).
- Kerala and Tamil Nadu need TLS handling. The ingest code should not disable certificate verification globally; it can pin a CA bundle or surface a "source unavailable" status.
- State lists add value mainly through timeliness, because they can appear before CDSCO's monthly list, and through items CDSCO omits.

### Gaps
- No official URL was found for the Telangana DCA web list, the Himachal Pradesh regulator list, or a current Karnataka DCD monthly list.
- The Kerala attachment format and the exact TN entries could not be read because both TLS fetches failed.
- No other state was surveyed (Gujarat, Punjab, West Bengal and others).

---

## Q5. Open datasets, GitHub scrapers, and CDSCO terms of use

### Takeaway
There is no official open dataset: searches of data.gov.in and Kaggle found nothing. Several 2026 GitHub projects scrape the CDSCO PDFs and the `publicNsqDrugTable` JSON, but most lack a licence and none publishes a complete, verified dataset. Blacklisted.co.in offers an all-months CSV ("Free to reuse with credit"). CDSCO's copyright policy requires permission for any reproduction and acknowledgement when its content is referred to.

### Cited Findings

**Table F: open data and scrapers**

| Project / dataset | What it offers | Licence / status | Source |
|---|---|---|---|
| Swa-hub/nsq-medicine-tracker | Downloader for CDSCO alert PDFs (default from 2019, `--start-year 2014`) plus a portal-JSON adapter (manual monthly capture). DuckDB warehouse. 3 s delay between files. | No licence shown; 1 commit | [GitHub](https://github.com/Swa-hub/nsq-medicine-tracker) |
| shayadmeri-svg/nsq | GET `cdscoonline.gov.in/CDSCO/publicNsqDrugTable` into Redis, with Streamlit dashboards | Licence not visible | [GitHub](https://github.com/shayadmeri-svg/nsq) |
| pranshurastogi/Nazar | CDSCO portal and PDFs, Tamil Nadu, Maharashtra, WHO. 1,404 alerts from 21 notices. Records on Arkiv. | MIT; live 18 Oct 2026 | [GitHub](https://github.com/pranshurastogi/Nazar) |
| shaurya703/safedose | ETL of the CDSCO Mar 2025 alert (70 batches, 64 medicines) | per search summary | [GitHub](https://github.com/shaurya703/safedose) |
| ShaikFayaz042/medicine-scanner-research | CDSCO and IPC/PvPI prototype. A search summary claims 395 files / 12,648 records, but the README does not show this. | No LICENSE file; 37 commits | [GitHub](https://github.com/ShaikFayaz042/medicine-scanner-research) |
| Saniya-Sayyad144/PharmaGuard | NSQ 2019 to 2026 analytics (SQL, Excel, Power BI) | per search summary | [GitHub](https://github.com/Saniya-Sayyad144/PharmaGuard-CDSCO-Drug-Quality-Analysis) |
| ibnweb3/recallops-india | Agent that holds distributor stock against real NSQ batches (synthetic stock) | per search summary | [GitHub](https://github.com/ibnweb3/recallops-india) |
| Blacklisted.co.in CSV | `https://blacklisted.co.in/data/nsq/all.csv` and per-month CSV, Jan 2019 to Aug 2026 | "Free to reuse with credit" | [Blacklisted](https://blacklisted.co.in/medicines/nsq) |
| data.gov.in / Kaggle | none found in two searches | n/a | [search results page set](https://www.outlookindia.com/healthcare-spotlight/112-drug-samples-declared-not-of-standard-quality-in-september-cdsco) |

- **CDSCO Copyright Policy**, quoted verbatim: "The contents of this website may not be reproduced partially or fully, without due permission from Central Drugs Standard Control Organization, Govt. of India." It continues: "If referred to as a part of another publication, the source must be appropriately acknowledged." And: "The contents of this website can not be used in any misleading or objectionable context." No last-updated date is shown. [CDSCO Copyright Policy](https://cdsco.gov.in/opencms/opencms/en/Copyright-Policy/)
- **eCDSCO portal terms** (hosted on statedrugs.gov.in) say the content should not be construed as a statement of law or used for legal purposes, and that reproduction for commercial purposes is not permitted without CDSCO's permission. [eCDSCO T&C](https://statedrugs.gov.in/SFDA/resources/app_srv/SFDA/global/helpfiles/Terms_Conditions_for_eCDSCO.pdf)
- **Scraper etiquette.** Swa-hub advises "Be polite to the government servers: keep the delay between requests and cache every file." [Swa-hub](https://github.com/Swa-hub/nsq-medicine-tracker)

### Inferences
- For a non-commercial college project, the defensible path is:
  - keep the index local;
  - store the source URL and fetch date for every row;
  - acknowledge CDSCO in the UI and the paper;
  - not republish bulk copies of CDSCO lists or the CSV without permission.
- If the dataset is released with the thesis, ask CDSCO for permission or publish only derived statistics. This is my reading of the copyright text, not legal advice.
- Third-party CSVs (Blacklisted) are useful as a cross-check but not as ground truth: the counts disagree (Q3), and the provenance is a secondary export.

### Gaps
- The cdsco.gov.in "Terms & Conditions", "Hyperlinking Policy" and "Disclaimer" pages are linked from the copyright page but were not read.
- I did not check whether any government open-data licence (for example, data.gov.in's) covers CDSCO alerts. It probably does not, since no dataset exists there, but this is unverified.
- Licences of most GitHub repos are unknown, and none of the code was inspected.
