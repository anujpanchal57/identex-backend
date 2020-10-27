default_bteam_name = "All Users"

default_bteam_id = "All_Users"

# 30 mins for requisition as well as auction
deadline_change_time_factor = 30 * 60

buyer_create_table = """CREATE TABLE IF NOT EXISTS `buyers` (
                      `buyer_id` int(11) NOT NULL AUTO_INCREMENT,
                      `company_name` varchar(100) NOT NULL,
                      `auto_join` tinyint(1) NOT NULL,
                      `domain_name` varchar(20) NOT NULL,
                      `company_logo` varchar(100) NOT NULL,
                      `default_currency` char(5) NOT NULL,
                      `subscription_plan` varchar(10) NOT NULL,
                      `activation_status` tinyint(1) NOT NULL,
                      `created_at` int(11) NOT NULL,
                      `updated_at` int(11) NOT NULL,
                      `city` varchar(100) NOT NULL DEFAULT '',
                      `business_address` varchar(500) NOT NULL DEFAULT '',
                      `pincode` varchar(20) NOT NULL DEFAULT '',
                      `gst_no` varchar(50) NOT NULL DEFAULT '',
                      `filing_frequency` varchar(20) NOT NULL DEFAULT '',
                      `gst_status` varchar(20) NOT NULL DEFAULT '',
                      `country` varchar(100) NOT NULL DEFAULT 'India',
                      `po_incr_factor` int(11) NOT NULL DEFAULT '1000',
                      `po_suffix` varchar(200) NOT NULL DEFAULT '',
                      `cin` varchar(200) NOT NULL DEFAULT '',
                      `company_email_address` varchar(200) NOT NULL DEFAULT '',
                      `company_contact_number` varchar(50) NOT NULL DEFAULT '',
                      PRIMARY KEY (`buyer_id`)
                    ) ENGINE=InnoDB AUTO_INCREMENT=1008 DEFAULT CHARSET=latin1"""

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

supplier_branches_create_table = """CREATE TABLE IF NOT EXISTS `supplier_branches` (
              `branch_id` int(11) NOT NULL AUTO_INCREMENT,
              `supplier_id` int(11) NOT NULL,
              `city` varchar(50) NOT NULL DEFAULT '',
              `business_address` varchar(500) NOT NULL DEFAULT '',
              `pincode` varchar(20) NOT NULL DEFAULT '',
              `country` varchar(100) NOT NULL DEFAULT 'India',
              PRIMARY KEY (`branch_id`),
              KEY `supplier_id` (`supplier_id`),
              CONSTRAINT `supplier_branches_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`)
            ) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=latin1"""

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
                savings float(20, 2) not null default 0,
                FOREIGN KEY (buyer_id) REFERENCES buyers(buyer_id)
            ) ENGINE=InnoDB auto_increment=1000"""

lots_create_table = """create table if not exists lots (
                lot_id int primary key not null auto_increment,
                requisition_id int not null, 
                lot_name varchar(50) not null, 
                lot_description varchar(500) not null default '', 
                force_lot_bidding bool not null,
                created_at int(11) not null,
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
                product_name varchar(500) not null,
                product_category varchar(500) not null default 'uncategorized', 
                product_sub_category varchar(500) not null default 'uncategorized',
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
                po_id int not null default 0,
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

# Not being used in the PO module
orders_create_table = """CREATE TABLE IF NOT EXISTS `orders` (
              `order_id` int(11) NOT NULL AUTO_INCREMENT,
              `po_no` varchar(50) NOT NULL,
              `product_id` int(11) NOT NULL,
              `payment_status` varchar(20) NOT NULL DEFAULT 'unpaid',
              `order_status` varchar(20) NOT NULL DEFAULT 'active',
              `grn_uploaded` tinyint(1) NOT NULL DEFAULT '0',
              `payment_date` int(11) NOT NULL DEFAULT '0',
              `delivery_date` int(11) NOT NULL DEFAULT '0',
              `transaction_ref_no` varchar(50) NOT NULL DEFAULT '',
              `created_at` int(11) NOT NULL,
              `product_description` varchar(500) NOT NULL DEFAULT '',
              `quantity` float(20,2) NOT NULL DEFAULT '0.00',
              `gst` float(20,2) NOT NULL DEFAULT '0.00',
              `per_unit` float(20,2) NOT NULL DEFAULT '0.00',
              `amount` float(20,2) NOT NULL DEFAULT '0.00',
              `delivery_time` int(11) NOT NULL DEFAULT '0',
              PRIMARY KEY (`order_id`)
            ) ENGINE=InnoDB AUTO_INCREMENT=1000"""

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

units_create_table = """create table if not exists units (
                unit_id varchar(50) not null,
                unit_name varchar(100) not null
            )"""

po_create_table = """CREATE TABLE IF NOT EXISTS `purchase_orders` (
                  `po_id` int(11) NOT NULL AUTO_INCREMENT,
                  `po_no` varchar(200) NOT NULL,
                  `buyer_id` int(11) NOT NULL,
                  `supplier_id` int(11) NOT NULL,
                  `acquisition_id` int(11) NOT NULL,
                  `acquisition_type` varchar(20) NOT NULL,
                  `order_date` int(11) NOT NULL,
                  `unit_currency` varchar(10) NOT NULL DEFAULT 'inr',
                  `total_amount` float(20,2) NOT NULL DEFAULT '0.00',
                  `total_gst` float(20,2) NOT NULL DEFAULT '0.00',
                  `notes` varchar(500) NOT NULL DEFAULT '',
                  `tnc` varchar(5000) NOT NULL DEFAULT '',
                  `po_url` varchar(500) NOT NULL DEFAULT '',
                  `supplier_gst_no` varchar(100) NOT NULL DEFAULT '',
                  `supplier_address` varchar(500) NOT NULL DEFAULT '',
                  `supplier_pincode` varchar(20) NOT NULL DEFAULT '',
                  `supplier_country` varchar(100) NOT NULL DEFAULT '',
                  `delivery_address` varchar(500) NOT NULL DEFAULT '',
                  `delivery_pincode` varchar(20) NOT NULL DEFAULT '',
                  `delivery_country` varchar(100) NOT NULL DEFAULT '',
                  `payment_terms` varchar(200) NOT NULL DEFAULT '',
                  `freight_included` varchar(200) NOT NULL DEFAULT '',
                  `prepared_by` varchar(200) NOT NULL DEFAULT '',
                  `approved_by` varchar(200) NOT NULL DEFAULT '',
                  `po_status` varchar(50) NOT NULL DEFAULT 'active',
                  `payment_status` varchar(50) NOT NULL DEFAULT 'unpaid',
                  `delivery_status` varchar(50) NOT NULL DEFAULT 'on_time',
                  `created_at` int(11) NOT NULL DEFAULT '0',
                  `total_in_words` varchar(1000) NOT NULL DEFAULT '',
                  `po_metadata` varchar(5000) NOT NULL DEFAULT '',
                  PRIMARY KEY (`po_id`),
                  KEY `buyer_id` (`buyer_id`),
                  KEY `supplier_id` (`supplier_id`),
                  CONSTRAINT `purchase_orders_ibfk_1` FOREIGN KEY (`buyer_id`) REFERENCES `buyers` (`buyer_id`),
                  CONSTRAINT `purchase_orders_ibfk_2` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`)
                ) ENGINE=InnoDB AUTO_INCREMENT=1016 DEFAULT CHARSET=latin1"""

sub_orders_create_table = """CREATE TABLE IF NOT EXISTS `sub_orders` (
                          `order_id` int(11) NOT NULL AUTO_INCREMENT,
                          `po_id` int(11) NOT NULL,
                          `product_id` int(11) NOT NULL,
                          `payment_status` varchar(20) NOT NULL DEFAULT 'unpaid',
                          `order_status` varchar(20) NOT NULL DEFAULT 'active',
                          `created_at` int(11) NOT NULL,
                          `product_description` varchar(500) NOT NULL DEFAULT '',
                          `quantity` float(20,2) NOT NULL DEFAULT '0.00',
                          `unit` varchar(40) NOT NULL DEFAULT '',
                          `gst` float(20,2) NOT NULL DEFAULT '0.00',
                          `per_unit` float(20,2) NOT NULL DEFAULT '0.00',
                          `amount` float(20,2) NOT NULL DEFAULT '0.00',
                          `delivery_time` int(11) NOT NULL DEFAULT '0',
                          `qty_received` float(20,2) NOT NULL DEFAULT '0.00',
                          `delivery_status` varchar(50) NOT NULL DEFAULT 'on_time',
                          `hsn` varchar(100) NOT NULL DEFAULT '',
                          `weight` float(20,2) NOT NULL DEFAULT '0.00',
                          `discount` float(20,2) NOT NULL DEFAULT '0.00',
                          PRIMARY KEY (`order_id`),
                          KEY `po_id` (`po_id`),
                          CONSTRAINT `sub_orders_ibfk_1` FOREIGN KEY (`po_id`) REFERENCES `purchase_orders` (`po_id`)
                        ) ENGINE=InnoDB AUTO_INCREMENT=1013 DEFAULT CHARSET=latin1"""

template_configs_create_table = """CREATE TABLE IF NOT EXISTS `template_configs` (
                                  `template_id` int(11) NOT NULL AUTO_INCREMENT,
                                  `buyer_id` int(11) NOT NULL,
                                  `template_name` varchar(300) NOT NULL,
                                  `template_type` varchar(50) NOT NULL DEFAULT 'purchase_order',
                                  `template_config` varchar(5000) NOT NULL,
                                  `updated_at` int(11) NOT NULL,
                                  PRIMARY KEY (`template_id`),
                                  KEY `buyer_id` (`buyer_id`),
                                  CONSTRAINT `template_configs_ibfk_1` FOREIGN KEY (`buyer_id`) REFERENCES `buyers` (`buyer_id`)
                                ) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=latin1"""