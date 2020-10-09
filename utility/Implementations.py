default_bteam_name = "All Users"

default_bteam_id = "All_Users"

# 30 mins for requisition as well as auction
deadline_change_time_factor = 30 * 60

buyer_create_table = """create table if not exists buyers (
                buyer_id int primary key not null auto_increment,
                company_name varchar(50) not null,
                auto_join bool not null,
                domain_name varchar(20) not null,
                company_logo varchar(100) not null,
                default_currency char(5) not null,
                subscription_plan varchar(10) not null,
                activation_status bool not null, 
                created_at int(11) not null,
                updated_at int(11) not null
            ) ENGINE=InnoDB auto_increment=1000"""

supplier_create_table = """create table if not exists suppliers (
                supplier_id int primary key not null auto_increment,
                company_name varchar(100) not null,
                company_logo varchar(100) not null,
                activation_status bool not null, 
                created_at int(11) not null,
                updated_at int(11) not null,
                annual_revenue varchar(50) not null default '',
                profile_completed bool not null default false,
                pan_no varchar(20) not null default '',
                company_nature varchar(30) not null default ''
            ) ENGINE=InnoDB auto_increment=1000"""

supplier_branches_create_table = """create table if not exists supplier_branches (
                branch_id int not null primary key auto_increment,
                supplier_id int not null,
                city varchar(50) not null default '',
                business_address varchar(500) not null default '',
                pincode varchar(20) not null default '',
                foreign key (supplier_id) references suppliers(supplier_id)
            ) Engine=InnoDB auto_increment=1000"""

supplier_industries_create_table = """create table if not exists supplier_industries (
                mapper_id int not null primary key auto_increment,
                supplier_id int not null,
                industry_id int not null,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
                FOREIGN KEY (industry_id) REFERENCES idntx_category(category_id)
            ) ENGINE=InnoDB auto_increment=1000"""

supplier_gst_details_create_table = """create table if not exists supplier_gst_details (
                gst_details_id int not null primary key auto_increment,
                supplier_id int not null,
                gst_no varchar(50) not null,
                filing_frequency varchar(20) not null default '',
                status varchar(20) not null default '',
                foreign key (supplier_id) references suppliers(supplier_id)
            ) Engine=InnoDB auto_increment=1000"""

buser_create_table = """create table if not exists b_users (
                email varchar(60) primary key not null,
                buyer_id int not null, 
                name char(60) not null, 
                mobile_no varchar(20) not null,
                password varchar(50) not null, 
                role varchar(10) not null,
                status bool not null, 
                created_at int(11) not null,
                updated_at int(11) not null,
                FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id)
            )"""

suser_create_table = """create table if not exists s_users (
                email varchar(60) primary key not null,
                supplier_id int not null,
                name char(60) not null, 
                mobile_no varchar(20) not null,
                password varchar(50) not null, 
                role varchar(10) not null, 
                status bool not null,
                created_at int(11) not null,
                updated_at int(11) not null,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
            )"""

authorizations_create_table = """create table if not exists authorizations (
                auth_id varchar(200) primary key not null,
                email varchar(60) not null,
                type varchar(10) not null, 
                entity_id varchar(10) not null, 
                device_name varchar(10), 
                logged_in int(11) not null,
                logged_out int(11) not null default 0,
                action_type varchar(20) not null default ""
            )"""

# Not done now
reqn_history_create_table = """create table if not exists requisition_history (
                reqn_id int primary key auto_increment not null,
                buyer_id int not null,
                product_name varchar(100) not null,
                product_description varchar(500) not null,
                category varchar(50) not null,
                quantity int not null,
                quantity_basis varchar(20) not null,
                created_at int(11) not null,
                FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id)
            )"""

supplier_relationship_create_table = """create table if not exists supplier_relationships (
                buyer_id int not null,
                supplier_id int not null,
                supplier_category varchar(100) not null default 'uncategorized',
                PRIMARY KEY (buyer_id, supplier_id)
            )"""

verification_tokens_create_table = """create table if not exists verification_tokens (
                token_id varchar(200) primary key not null,
                token_name varchar(20) not null, 
                user_id varchar(60) not null, 
                user_type varchar(20) not null
            )"""

requisition_create_table = """create table if not exists requisitions (
                requisition_id int primary key not null auto_increment,
                buyer_id int not null,
                requisition_name varchar(50) not null,
                timezone varchar(50) not null,
                currency varchar(3) not null, 
                deadline int(11) not null, 
                utc_deadline varchar(20) not null,
                supplier_instructions varchar(500) not null,
                tnc varchar(500) not null,
                cancelled bool not null,
                request_type varchar(20) not null,
                status bool not null,
                created_at int(11) not null,
                submission_limit int not null default 3,
                ref_no varchar(100) not null default '',
                budget float(20, 2) not null default 0,
                FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id)
            ) ENGINE=InnoDB auto_increment=1000"""

lots_create_table = """create table if not exists lots (
                lot_id int primary key not null auto_increment,
                requisition_id int not null, 
                lot_name varchar(50) not null, 
                lot_description varchar(500) not null default '', 
                force_lot_bidding bool not null,
                created_at int(11) not null,
                lot_category int not null default 0,
                lot_sub_category int not null default 0,
                FOREIGN KEY (requisition_id) REFERENCES requisitions(requisition_id)
            ) ENGINE=InnoDB auto_increment=1000"""

products_create_table = """create table if not exists products (
                reqn_product_id int primary key not null auto_increment,
                product_id int not null, 
                lot_id int not null,
                buyer_id int not null,  
                product_description varchar(500) not null, 
                quantity float not null, 
                unit varchar(40) not null,
                FOREIGN KEY (lot_id) REFERENCES lots(lot_id),
                FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id),
                FOREIGN KEY (product_id) REFERENCES product_master(product_id)
            ) ENGINE=InnoDB auto_increment=1000"""

product_master_create_table = """create table if not exists product_master (
                product_id int primary key not null auto_increment,
                buyer_id int not null,  
                product_name varchar(50) not null,
                product_category int not null default 0, 
                product_sub_category int not null default 0,
                created_at int(11) not null,
                FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id)
            ) ENGINE=InnoDB auto_increment=1000"""

documents_create_table = """create table if not exists documents (
                document_id int primary key not null auto_increment,
                operation_id int not null, 
                operation_type varchar(10) not null, 
                document_url varchar(100) not null,
                document_type varchar(20) not null, 
                document_name varchar(100) not null, 
                uploaded_on int(11) not null, 
                uploaded_by varchar(60) not null, 
                uploader varchar(50) not null
            ) ENGINE=InnoDB auto_increment=1000"""

invited_suppliers_create_table = """create table if not exists invited_suppliers (
                invite_id int primary key not null auto_increment,
                operation_id int not null, 
                operation_type varchar(10) not null, 
                supplier_id int not null, 
                invited_on int(11) not null, 
                unlock_status bool not null, 
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
                FOREIGN KEY (operation_id) REFERENCES requisitions(requisition_id)
            ) ENGINE=InnoDB auto_increment=1000"""

quotations_create_table = """create table if not exists quotations (
                quotation_id int primary key auto_increment,
                supplier_id int not null, 
                requisition_id int not null,  
                total_amount float(11, 2) not null, 
                total_gst float(11, 2) not null,
                quote_validity int(11) not null, 
                status bool not null, 
                created_at int(11) not null, 
                payment_terms int not null default 0,
                remarks varchar(500) not null default '',
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
                FOREIGN KEY (requisition_id) REFERENCES requisitions(requisition_id)
            ) ENGINE=InnoDB auto_increment=1000"""

quotes_create_table = """create table if not exists quotes (
                quote_id int primary key not null auto_increment,
                quotation_id int not null, 
                charge_id int not null, 
                charge_name varchar(50) not null, 
                quantity float(11,2) not null, 
                gst float(5,2) not null, 
                per_unit float(11, 2) not null, 
                amount float(11, 2) not null,
                delivery_time int not null, 
                confirmed bool not null,
                logistics_included bool not null default false,
                FOREIGN KEY (quotation_id) REFERENCES quotations(quotation_id),
                FOREIGN KEY (charge_id) REFERENCES products(reqn_product_id)
            ) ENGINE=InnoDB auto_increment=1000"""

activity_logs_create_table = """create table if not exists activity_logs (
                activity_id int primary key not null auto_increment,
                activity varchar(100) not null, 
                done_by varchar(60) not null,
                name varchar(60) not null,
                company_name varchar(50) not null,
                user_id int not null,
                type_of_user varchar(10) not null,
                operation_id int not null, 
                operation_type varchar(10) not null,
                ip_address varchar(50) not null, 
                timestamp int(11) not null
            ) ENGINE=InnoDB auto_increment=1000"""

messages_create_table = """create table if not exists messages (
                message_id int primary key auto_increment not null, 
                operation_id int not null, 
                operation_type varchar(20) not null, 
                message varchar(500) not null, 
                sent_on int(11) not null, 
                sender_user varchar(60) not null, 
                sent_by int not null, 
                sender varchar(20) not null,
                received_by int not null, 
                receiver varchar(20) not null, 
                status bool not null
            ) ENGINE=InnoDB auto_increment=1000"""

message_documents_create_table = """create table if not exists message_documents (
                document_id int primary key not null auto_increment,
                operation_id int not null, 
                operation_type varchar(10) not null,
                entity_id int not null, 
                document_url varchar(100) not null,
                document_type varchar(20) not null, 
                document_name varchar(100) not null, 
                uploaded_on int(11) not null, 
                uploaded_by varchar(60) not null, 
                uploader varchar(50) not null
            ) ENGINE=InnoDB auto_increment=1000"""

orders_create_table = """create table if not exists orders (
                order_id int primary key not null auto_increment,
                buyer_id int not null, 
                supplier_id int not null,
                po_no varchar(50) not null,
                acquisition_id int not null default 0, 
                acquisition_type varchar(20) not null default '',
                quote_id int not null,
                reqn_product_id int not null,
                payment_status varchar(20) not null default 'unpaid', 
                order_status varchar(20) not null default 'active',
                grn_uploaded bool not null default false,
                payment_date int(11) not null default 0,
                delivery_date int(11) not null default 0,
                transaction_ref_no varchar(50) not null default '',
                created_at int(11) not null,
                remarks varchar(200) not null default '',
                saved_amount float(11, 2) not null default 0,
                FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
            ) ENGINE=InnoDB auto_increment=1000"""

invoices_create_table = """create table if not exists invoices (
                invoice_id int not null primary key auto_increment,
                invoice_no varchar(100) not null,
                supplier_id int not null,
                buyer_id int not null,
                total_gst float(11, 2) not null,
                total_amount float(11, 2) not null,
                created_at int(11) not null,
                payment_details varchar(500) not null,
                due_date int(11) not null default 0,
                paid bool not null default false,
                FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
            ) ENGINE=InnoDB auto_increment=1000"""

invoice_line_items_create_table = """create table if not exists invoice_line_items (
                line_item_id int primary key not null auto_increment,
                invoice_id int not null, 
                order_id int not null, 
                quantity float(11, 2) not null, 
                gst float(11, 2) not null, 
                per_unit float(11, 2) not null, 
                amount float(11, 2) not null,
                unit_currency varchar(3) not null, 
                FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id),
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            ) ENGINE=InnoDB auto_increment=1000"""

ratings_create_table = """create table if not exists ratings (
                rating_id int primary key not null auto_increment,
                client_id int not null,
                client_type varchar(20) not null,
                receiver_id int not null,
                receiver_type varchar(20) not null,
                acquisition_id int not null,
                acquisition_type varchar(20) not null,
                rating float not null,
                updated_at int(11) not null,
                review varchar(500) not null default ''
            ) ENGINE=InnoDB auto_increment=1000"""

pincodes_create_table = """create table if not exists pincodes (
                pincode_id int not null primary key auto_increment,
                pincode varchar(20) not null,
                division_name varchar(60) not null default '',
                region_name varchar(60) not null default '',
                circle_name varchar(60) not null default '',
                taluka varchar(60) not null default '',
                district_name varchar(60) not null default '',
                state_name varchar(60) not null default ''
            ) ENGINE=InnoDB"""

projects_create_table = """create table if not exists projects(
                project_id int not null primary key auto_increment,
                project_name varchar(100) not null,
                project_description varchar(500) not null default '',
                project_budget float(20, 2) not null default 0,
                project_deadline int(11) not null,
                project_utc_deadline varchar(20) not null default '',
                ref_id varchar(100) not null default ''
            ) Engine=InnoDB auto_increment=1000"""

project_members_create_table = """create table if not exists project_members (
                project_id int not null,
                member_email varchar(60) not null,
                primary key (project_id, member_email)
            )"""

project_lots_create_table = """create table if not exists project_lots (
                project_id int not null,
                lot_id int not null,
                primary key (project_id, lot_id)
            )"""

logs_create_table = """create table if not exists logs (
                log_id varchar(100) not null primary key,
                function_name varchar(50) not null,
                module_name varchar(50) not null, 
                message varchar(1000) not null, 
                priority varchar(10) not null, 
                timestamp int(11) not null
            )"""