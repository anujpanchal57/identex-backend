default_bteam_name = "All Users"

default_bteam_id = "All_Users"

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
                company_name varchar(50) not null,
                company_logo varchar(100) not null,
                activation_status bool not null, 
                created_at int(11) not null,
                updated_at int(11) not null
            ) ENGINE=InnoDB auto_increment=1000"""

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
                supplier_instructions varchar(500) not null,
                tnc varchar(500) not null,
                cancelled bool not null,
                status bool not null,
                created_at int(11) not null,
                FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id)
            ) ENGINE=InnoDB auto_increment=1000"""

lots_create_table = """create table if not exists lots (
                lot_id int primary key not null auto_increment,
                requisition_id int not null, 
                lot_name varchar(50) not null, 
                lot_description varchar(500) not null, 
                force_lot_bidding bool not null,
                created_at int(11) not null,
                FOREIGN KEY (requisition_id) REFERENCES requisitions(requisition_id)
            ) ENGINE=InnoDB auto_increment=1000"""

products_create_table = """create table if not exists products (
                product_id int primary key not null auto_increment,
                lot_id int not null,
                buyer_id int not null,  
                product_name varchar(50) not null,
                product_category varchar(50) not null, 
                product_description varchar(500) not null, 
                quantity int not null, 
                unit varchar(40) not null,
                created_at int(11) not null,
                FOREIGN KEY (lot_id) REFERENCES lots(lot_id),
                FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id)
            ) ENGINE=InnoDB auto_increment=1000"""

documents_create_table = """create table if not exists documents (
                document_id int primary key not null auto_increment,
                operation_id int not null, 
                operation_type varchar(10) not null, 
                document_url varchar(100) not null,
                document_type varchar(20) not null, 
                document_name varchar(20) not null, 
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
                remarks varchar(500) not null,
                quote_validity int(11) not null, 
                delivery_time int not null, 
                total_amount float(11, 2) not null, 
                total_gst float(11, 2) not null, 
                status bool not null, 
                created_at int(11) not null, 
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
                FOREIGN KEY (requisition_id) REFERENCES requisitions(requisition_id)
            ) ENGINE=InnoDB auto_increment=1000"""

quotes_create_table = """create table if not exists quotes (
                quote_id int primary key not null auto_increment,
                quotation_id int not null, 
                charge_id int not null, 
                charge_name varchar(50) not null, 
                quantity int not null, 
                gst int not null, 
                per_unit float(11, 2) not null, 
                amount float(11, 2) not null, 
                FOREIGN KEY (quotation_id) REFERENCES quotations(quotation_id),
                FOREIGN KEY (charge_id) REFERENCES products(product_id)
            ) ENGINE=InnoDB auto_increment=1000"""

activity_logs_create_table = """create table if not exists activity_logs (
                activity_id int primary key not null auto_increment,
                activity varchar(100) not null, 
                done_by varchar(60) not null, 
                type_of_user varchar(10) not null,
                operation_id int not null, 
                operation_type varchar(10) not null,
                ip_address varchar(50) not null, 
                timestamp int(11) not null
            ) ENGINE=InnoDB auto_increment=1000"""

logs_create_table = """create table if not exists logs (
                log_id varchar(100) not null primary key,
                function_name varchar(50) not null,
                module_name varchar(50) not null, 
                message varchar(1000) not null, 
                priority varchar(10) not null, 
                timestamp int(11) not null
            )"""