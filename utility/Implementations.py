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
                FOREIGN KEY (buyer_id) REFERENCES buyers(_id)
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
                FOREIGN KEY (supplier_id) REFERENCES suppliers(_id)
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
                FOREIGN KEY (buyer_id) REFERENCES buyers(_id)
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

requisition_create_table = """create table if not exists """

logs_create_table = """create table if not exists logs (
                log_id varchar(100) not null primary key,
                function_name varchar(50) not null,
                module_name varchar(50) not null, 
                message varchar(1000) not null, 
                priority varchar(10) not null, 
                timestamp int(11) not null
            )"""