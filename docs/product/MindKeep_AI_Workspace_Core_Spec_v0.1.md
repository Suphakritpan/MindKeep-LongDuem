อันนี้คือ สเปกหลักก่อนทำ Master Prompt สำหรับโปรเจ็ค MindKeep AI Workspace · ลองดื่ม โดยแกนหลักคือเอา dataset บริษัท SME “ลองดื่ม / LongDuem” เข้าเป็น workspace จริงในระบบ และทำ MVP ที่โฟกัสแผนก Finance & Accounting ของ ป้าต้อย สุขสม ก่อน ส่วนแผนกอื่นยังคงมีไว้เพื่อทดสอบ Work Memory, permission, RAG และ handover ให้เหมือนการใช้งานจริงของบริษัทหนึ่ง ไม่ใช่ mockup UI ธรรมดา ข้อมูลตั้งต้นของลองดื่มมี company profile, ทีม 4 แผนก และ Work Memory เดิมอยู่แล้ว ส่วน Feature Design ระบุชัดว่าระบบมี 4 แผนกเชื่อมด้วย Work Memory และฟีเจอร์ Finance หลักคือ Bill Scanner, Income & Expense Summary, VAT Calculator, Financial Insight และ Tax Estimate

MindKeep AI Workspace · LongDuem Core Specification v0.1
1. เป้าหมายของระบบ

ระบบนี้ต้องจำลองว่า ลองดื่ม / LongDuem เป็นบริษัท SME ที่เข้ามาใช้งาน MindKeep จริงใน environment สำหรับ demo/dev โดยทุกอย่างต้องผ่านระบบจริง ตั้งแต่ login, organization, department, user, role, permission, API, database, activity log, Work Memory, RAG และ frontend ห้ามสร้างเป็นข้อมูล hardcode ฝั่ง frontend แบบโชว์อย่างเดียว

เป้าหมายหลักของ MindKeep คือทำให้ทุก action สำคัญของพนักงานกลายเป็น Work Memory ขององค์กร พอพนักงานลาออก ป่วย เกษียณ หรือเปลี่ยนตำแหน่ง ความรู้ วิธีทำงาน ตัวเลข เอกสาร และบริบทธุรกิจจะยังอยู่ในระบบให้คนถัดไปค้นหาและถาม AI ได้

2. Scope ของ MVP

MVP รอบนี้ไม่ต้องทำทุกแผนกลึกเท่ากัน ให้โฟกัสที่ บัญชีและการเงิน / Finance & Accounting ของ ป้าต้อย สุขสม เป็นหลัก เพราะเป็นแผนกที่มี workflow ชัดและพิสูจน์คุณค่าของระบบได้เร็วที่สุด ได้แก่ สแกนบิล บันทึกรายรับรายจ่าย คำนวณ VAT สรุป P&L วิเคราะห์ CSV และประมาณการภาษี

แผนกอื่นยังต้องมีอยู่จริงในระบบเพื่อให้ workspace สมจริงและใช้ทดสอบขอบเขตข้อมูล ได้แก่ Farm & Production, Legal & Procurement, และ Marketing & Delivery แต่ฟีเจอร์ของแผนกเหล่านั้นในรอบแรกให้เป็น seeded knowledge, activity log, profile, risk/handover และ basic RAG query ก่อน ไม่ต้อง build tool ครบทุกตัว

3. LongDuem เป็น real demo tenant

ต้องสร้าง organization ชื่อ ลองดื่ม / LongDuem เป็น tenant จริงใน database มีข้อมูลบริษัท เช่น ประเภทธุรกิจน้ำมะพร้าวแท้ 100% แบบ Farm-to-Business, ที่ตั้ง, ปีที่ก่อตั้ง, พื้นที่สวน 22 ไร่, มะพร้าว 380 ต้น, พนักงาน 4 คน, รายได้ประมาณ 2.8 ล้านบาทต่อปี และสินค้า น้ำมะพร้าวสด น้ำมะพร้าว UHT มะพร้าวอ่อน สโลแกนของบริษัทคือ "ลองดื่ม — Fresh coconut water is good for your health. Try it!" ใช้เป็น tagline หลักของแบรนด์ในทุกจุดที่แสดงชื่อบริษัท เช่น workspace header, marketing material, และหน้า dashboard

คำว่า demo/mock/sample ห้ามโชว์ในหน้า user ปกติ แต่ใน backend สามารถ mark ได้ว่าเป็น seed data เช่น seed_source = longduem_dataset, seed_environment = demo, is_seed_data = true เพื่อให้ reset และ seed ซ้ำได้ง่าย

4. Organization Structure

ระบบต้องมี 4 departments จริงภายใต้ LongDuem โดยแต่ละแผนกมี memory collection แยกกัน

Farm & Production ใช้ memory_farm เจ้าของข้อมูลหลักคือตาชัย มั่นคง

Finance & Accounting ใช้ memory_finance เจ้าของข้อมูลหลักคือป้าต้อย สุขสม และเป็น MVP focus

Legal & Procurement ใช้ memory_legal เจ้าของข้อมูลหลักคือลุงศักดิ์ วงศ์ใหญ่

Marketing & Delivery ใช้ memory_marketing เจ้าของข้อมูลหลักคือหนูดี รักไทย

ทุกข้อมูลต้องผูกด้วย organization_id, department_id, user_id หรือ owner_user_id เพื่อให้ permission และ RAG filtering ทำงานได้จริง

5. Users, Roles, Permission

ต้องสร้าง user จริงในระบบ ไม่ใช่ card mockup ได้แก่ ตาชัย, ป้าต้อย, ลุงศักดิ์, หนูดี และควรมี account ระดับ owner/admin ของลองดื่มอีก 1 คนสำหรับทดสอบการเห็นข้อมูลข้ามแผนก

permission ขั้นต่ำคือ พนักงานทั่วไปเห็นข้อมูลแผนกตัวเองเท่านั้น ป้าต้อยเห็นข้อมูล Finance & Accounting ลุงศักดิ์เห็น Legal & Procurement หนูดีเห็น Marketing & Delivery ตาชัยเห็น Farm & Production ส่วน owner/admin เห็นได้ทุกแผนก AI chat และ RAG ต้องใช้ permission rule เดียวกับ API ถ้า user ไม่มีสิทธิ์เห็น finance memory, AI ก็ต้องไม่มีสิทธิ์ retrieve finance memory เช่นกัน

6. Cleanup ข้อมูลเก่า

ก่อน seed LongDuem ต้องลบข้อมูล demo เก่าออกแบบปลอดภัย ห้าม truncate database ทั้งหมด ให้ลบเฉพาะ old business seed data เช่น organization เก่า department เก่า user seed เก่า document seed เก่า work memory เก่า activity log เก่า chat session เก่า handover report เก่า และ vector collection เก่าที่เป็น demo เดิม

ห้ามลบ migration table, base role, system settings, auth config, admin framework data หรือข้อมูล infrastructure ที่ทำให้ระบบพัง seed script ต้อง idempotent คือรันซ้ำแล้วไม่เกิดข้อมูลซ้ำ และต้อง replace LongDuem dataset ได้อย่างปลอดภัย

7. Core Data Flow

ทุกฟีเจอร์ต้องเดิน flow เดียวกันคือ User Action → Backend Service → Structured Record → Activity Log → Work Memory → Vector/RAG Metadata → AI Query Source

ตัวอย่างเช่น ป้าต้อยอัปโหลดบิล ระบบต้องสร้าง file asset ก่อน จากนั้น extract ข้อมูลบิล จัดหมวด คำนวณ VAT Input ให้ user review แล้วค่อย confirm เป็น transaction หลัง confirm ต้องสร้าง activity log และบันทึก summary ลง memory_finance จากนั้นจึงส่งเข้า vector store เพื่อให้ AI ค้นได้ภายใต้ permission ที่ถูกต้อง

8. Finance MVP Features
8.1 Bill Scanner

Bill Scanner ต้องรองรับรูปถ่ายบิลและ PDF ใบเสร็จ ระบบต้องดึงข้อความด้วย PDF parser หรือ OCR adapter แล้วให้ AI จัดหมวดค่าใช้จ่าย เช่น วัตถุดิบ บรรจุภัณฑ์ ค่าขนส่ง สาธารณูปโภค ค่าแรง การตลาด และอื่นๆ จากนั้นคำนวณ VAT Input

ผลลัพธ์ต้องไม่ auto-confirm ทันที ต้องมีหน้า review ให้ป้าต้อยแก้ vendor, วันที่, รายการ, subtotal, VAT, total, category และ note ก่อนกดบันทึกจริง เมื่อ confirm แล้วจึงสร้าง finance transaction, activity log และ memory_finance

8.2 Income & Expense Summary

ระบบต้องให้เลือกช่วงเวลาและบันทึกรายรับตามช่องทาง เช่น Shopee, LINE OA, ส่งตรง, Lazada, Modern Trade และอื่นๆ จากนั้นรวมกับค่าใช้จ่ายที่ confirm แล้วใน transactions เพื่อคำนวณรายรับ รายจ่าย กำไรขั้นต้น margin percentage และเปรียบเทียบกับช่วงก่อนหน้า

AI ต้องเขียน executive summary ภาษาไทย เช่น เดือนนี้กำไรเพิ่มหรือลดเพราะอะไร รายจ่ายหมวดไหนสูงผิดปกติ ช่องทางไหนสร้างรายได้มากสุด และควรทำอะไรต่อ ผลสรุปต้องบันทึกเป็น financial report และ memory_finance

8.3 VAT Calculator & Alert

ระบบต้องคำนวณ VAT รายเดือนจากรายรับและใบเสร็จที่มี VAT Input โดยใช้สูตรใน MVP คือ VAT ขาย = รายรับรวม × 7/107, VAT ซื้อ = ผลรวม VAT Input จากบิลที่ confirm แล้ว, VAT สุทธิ = VAT ขาย - VAT ซื้อ

ต้องสร้าง VAT period รายเดือน มี due date วันที่ 15 ของเดือนถัดไป และสร้าง alert ล่วงหน้า 5 วันก่อนครบกำหนด ทุกผลลัพธ์ต้องมี disclaimer ว่าเป็นการคำนวณเพื่อช่วยเตรียมข้อมูลและควรตรวจสอบกับผู้ทำบัญชีหรือผู้เชี่ยวชาญก่อนยื่นจริง

8.4 Financial Insight

ระบบต้องรับ CSV ยอดขายหรือข้อมูลการเงิน แล้วใช้ pandas วิเคราะห์ trend เช่น เดือนที่ดีที่สุด เดือนที่แย่ที่สุด ช่องทางรายได้หลัก สินค้าที่ margin สูงสุด ค่าใช้จ่ายที่โตผิดปกติ และ pattern ที่ควรสนใจ

หลังวิเคราะห์ตัวเลขแล้ว AI ต้องเขียนสรุปภาษาไทยและคำแนะนำ 3 ข้อ ผลลัพธ์ต้องถูกเก็บเป็น financial insight report, activity log และ memory_finance

8.5 Tax Estimate

ระบบต้องรับกำไรสุทธิสะสมและรายการค่าใช้จ่ายที่หักได้ แล้วคำนวณประมาณการภาษีเงินได้นิติบุคคลด้วย tax config ที่แก้ไขได้ ไม่ควรกระจายสูตรภาษีไว้ใน frontend

ผลลัพธ์ต้องมีประมาณการ CIT, เงินสำรองที่ควรเตรียม, คำแนะนำก่อนสิ้นปีบัญชี และ disclaimer ทุกครั้งว่าเป็นการประมาณการ ไม่ใช่คำปรึกษาภาษีอย่างเป็นทางการ

9. Database Specification ระดับหลัก

ตารางหลักที่ต้องมีหรือปรับให้รองรับ ได้แก่ organizations, departments, users, roles, user_department_roles, file_assets, finance_documents, bill_extractions, finance_transactions, transaction_categories, income_channels, vat_periods, financial_reports, tax_estimates, activity_logs, work_memories, chat_sessions, chat_messages, handover_reports, notifications, audit_logs

ฝั่ง Finance ทุก record ต้องผูกกับ organization_id, department_id, created_by_user_id และถ้ามีที่มาเพิ่มเติมต้องผูกกับ source_file_id, activity_id, memory_id หรือ source_id ด้วย เพื่อให้ trace ย้อนกลับได้ว่า memory นี้เกิดจาก action ไหน ไฟล์ไหน และใครเป็นคนทำ

10. Work Memory Specification

Work Memory คือชั้นความรู้กลางของระบบ แต่ต้องไม่เป็นแค่ text blob เฉยๆ แต่ละ memory item ควรมี title, content, summary, organization_id, department_id, owner_user_id, source_type, source_id, tags, importance, visibility_scope, embedding_status, created_at

สำหรับ finance action ทุกตัวที่สำคัญต้องสร้าง memory_finance ได้แก่ bill_confirmed, expense_recorded, income_recorded, pnl_summary_generated, vat_calculated, financial_insight_generated, tax_estimate_generated

11. RAG / Vector Store Specification

ต้องสร้าง vector collection หรือ namespace ตามแผนก ได้แก่ memory_farm, memory_finance, memory_legal, memory_marketing โดยทุก vector item ต้องมี metadata อย่างน้อยคือ organization_id, department_id, owner_user_id, source_type, source_id, tags, importance, visibility_scope

เวลา AI chat ค้นข้อมูล ต้อง filter ด้วย organization_id และ allowed department_id ก่อนเสมอ ถ้า user เป็น Finance จะค้นได้เฉพาะ memory_finance ถ้าเป็น admin ถึงจะค้นข้ามแผนกได้ ห้ามใช้ prompt กลางที่มีข้อมูลทุกแผนกแล้วปล่อยให้ AI เลือกเอง เพราะเสี่ยง data leakage

12. Backend/API Specification

API ต้องเป็นแหล่งข้อมูลหลักของ frontend ห้ามให้ frontend import array mock ข้อมูล LongDuem โดยตรง endpoint หลักที่ควรมีใน MVP คือ workspace current, departments, employees, finance bill upload, bill extract, bill confirm, transactions, income entry, finance summary, VAT calculate, VAT periods, financial insight CSV upload, tax estimate, memory list และ chat endpoint

รูปแบบ API ต้องบังคับ auth และ permission ทุก endpoint โดยเฉพาะ finance endpoint เช่น user ที่ไม่ใช่ Finance หรือ admin ห้ามเรียกดู transaction, bill, VAT, report และ memory_finance

13. Frontend Specification

หน้า frontend ต้องทำงานเหมือน workspace จริงของบริษัทลองดื่ม หน้าแรกควรแสดง workspace dashboard ที่ดึงชื่อบริษัท แผนก พนักงาน และ activity ล่าสุดจาก API

MVP Finance ต้องมีหน้า Finance Dashboard, Bill Scanner, Bill Review, Transaction List, Income & Expense Summary, VAT Calculator, Financial Insight Upload, Tax Estimate, Work Memory และ AI Chat Popup ทุกหน้าต้อง fetch API จริงและแสดง loading/error/empty state อย่างชัดเจน

ใน UI ห้ามแสดงคำว่า mock/fake/sample และห้าม hardcode ข้อความ dataset ใน component ยกเว้น label static ของระบบ เช่นชื่อเมนูหรือหัวข้อฟีเจอร์

14. Activity Log และ Audit

Activity Log ใช้เพื่อให้ user เห็นประวัติการทำงาน เช่น ป้าต้อยอัปโหลดบิล ยืนยันค่าใช้จ่าย สรุปรายรับรายจ่าย คำนวณ VAT หรือสร้าง tax estimate

Audit Log ใช้เพื่อความปลอดภัย เช่น ใครเปิดดู finance document, ใครแก้ transaction, ใคร export report, ใครถาม AI แล้ว retrieve memory อะไร โดยเฉพาะข้อมูลบัญชีต้องเก็บ audit ให้มากกว่าข้อมูลทั่วไป

15. Sensitive Mock Data Rule

แม้ข้อมูลนี้เป็น demo/dev แต่ระบบต้อง treat เป็นข้อมูลธุรกิจจริง ใช้เลขง่ายๆแทนข้อมูล sensitive เช่น supplier phone เป็น 080-000-1001, bank account เป็น 111-1-11111-1, username เป็น longduem.finance.demo

ห้ามเก็บ password plaintext ถ้ามี credential reference ให้ใช้ stored_in_secure_vault หรือ credential_reference_only และ AI ไม่ควรเปิดเผยข้อมูลลักษณะ credential หรือข้อมูลที่ไม่เกี่ยวกับคำถาม

16. Testing Specification

ต้องมี test ระดับ seed, backend, API, permission, RAG และ frontend integration อย่างน้อยต้องทดสอบว่า cleanup ลบข้อมูลเก่าได้โดยไม่ลบ system table, seed ซ้ำไม่ duplicate, LongDuem organization มีจริง, departments ครบ 4, users ผูก department ถูกต้อง, ป้าต้อยเข้าถึง finance ได้, user แผนกอื่นเข้าถึง finance private memory ไม่ได้, admin เข้าถึงทุกแผนกได้

ฝั่ง Finance ต้อง test flow อัปโหลดบิล → extract → review → confirm → transaction → activity log → memory_finance, test VAT formula, test due date วันที่ 15 เดือนถัดไป, test alert ล่วงหน้า 5 วัน, test CSV insight, test tax estimate disclaimer และ test ว่า AI chat retrieve เฉพาะ source ที่ user มีสิทธิ์

17. Priority Implementation Plan

Priority 1 คือ cleanup ข้อมูลเก่าและ seed LongDuem tenant ให้เป็น active workspace จริง

Priority 2 คือสร้าง departments, users, roles, permission และ memory collection mapping

Priority 3 คือสร้าง finance data model และ seed finance knowledge ของป้าต้อย

Priority 4 คือทำ Bill Scanner MVP แบบ upload, extract, review, confirm, transaction, memory

Priority 5 คือทำ Income & Expense Summary และ finance dashboard

Priority 6 คือทำ VAT Calculator & Alert

Priority 7 คือทำ Financial Insight และ Tax Estimate

Priority 8 คือเชื่อม Work Memory, RAG, AI Chat และ permission filtering ให้ครบ

Priority 9 คือปรับ frontend ทุกหน้าให้ดึง API จริง ลบ hardcoded mock เก่า และเพิ่ม tests/evaluation end-to-end

18. Acceptance Criteria หลัก

ระบบจะถือว่าผ่านสเปกหลักเมื่อ LongDuem เป็น workspace จริงในระบบ dev/demo ข้อมูลเก่าถูกลบอย่างปลอดภัย ข้อมูลใหม่ทั้งหมดเชื่อมกันด้วย organization, department, user และ role จริง Finance MVP ทำงานครบตั้งแต่อัปโหลดบิลจนถึงบันทึกลง memory_finance AI chat ค้นข้อมูลจาก RAG ตาม permission เท่านั้น และ frontend ไม่มี hardcoded dataset เก่าเหลืออยู่

สรุปสั้นๆคือ สเปกนี้กำหนดว่าเราจะไม่ทำ “หน้า demo ลองดื่ม” แต่จะทำ “ระบบ MindKeep ที่บริษัทลองดื่มเข้ามาใช้งานจริงใน demo environment” โดย MVP ใช้บัญชีและการเงินของป้าต้อยเป็นตัวพิสูจน์ระบบก่อน แล้วใช้ Work Memory เป็นแกนกลางของทั้งองค์กร