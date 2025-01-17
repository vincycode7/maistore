from models.models_helper import *


class ProductSubCatModel(db.Model, ModelsHelper):
    __tablename__ = "productsubcat"

    # columns
    id = db.Column(db.Integer, primary_key=True, unique=True)
    # gatta change this to productcatid
    category_id = db.Column(db.Integer, db.ForeignKey("productcat.id"), nullable=False)
    desc = db.Column(db.String(256), unique=False, nullable=False)

    # merge
    products = db.relationship(
        "ProductModel",
        lazy="dynamic",
        backref="productsubcat",
        cascade="all, delete-orphan",
    )

    productsize = db.relationship(
        "ProductSizeModel",
        lazy="dynamic",
        backref="productsubcat",
        cascade="all, delete-orphan",
    )

    @classmethod
    def find_by_subcatdesc(
        cls, subcatdesc=None, get_err="product_subcat_err_find_by_desc"
    ):
        try:
            result = cls.query.filter_by(desc=subcatdesc).first()
        except Exception as e:
            raise ProductSubCatException(gettext(get_err).format(e))
        except:
            raise ProductSizeException(gettext(get_err))
        return result

    @classmethod
    def find_by_subcatdesc_catid(
        cls,
        subcatdesc=None,
        productcat_id=None,
        get_err="product_subcat_err_find_by_desc_id",
    ):
        try:
            result = cls.query.filter_by(
                desc=subcatdesc, category_id=productcat_id
            ).first()
        except Exception as e:
            raise ProductSubCatException(gettext(get_err).format(e))
        except:
            raise ProductSizeException(gettext(get_err))
        return result

    @classmethod
    def check_unique_inputs(cls, subcat_data=None):
        desc = cls.find_by_subcatdesc(subcatdesc=subcat_data.get("desc", None))
        subcatdesc_catid = cls.find_by_subcatdesc_catid(
            subcatdesc=subcat_data.get("desc", None),
            productcat_id=subcat_data.get("category_id", None),
        )
        productcat = cls.find_productcat_by_id(
            productcat_id=subcat_data.get("category_id", None)
        )
        return subcatdesc_catid, desc, productcat

    @classmethod
    def post_unique_already_exist(cls, subcat_data):
        subcatdesc_catid, _, productcat = cls.check_unique_inputs(
            subcat_data=subcat_data
        )

        # check subcat permission, edit and parse data
        msg, status_code, _ = cls.auth_by_admin_root(
            get_err="product_subcat_req_ad_priv_to_post"
        )
        if status_code != 200:
            return msg, status_code

        if subcatdesc_catid:
            return {
                "message": gettext("product_subcat_for_cat_exist")
            }, 400  # 400 is for bad request

        # check if productid exist
        if not productcat:
            return {"message": gettext("product_cat_not_found")}, 404
        return False, 200

    @classmethod
    def put_unique_already_exist(cls, subcat_id, subcat_data):
        productsubcat = cls.find_by_id(id=subcat_id)
        subcatdesc_catid, _, productcat = cls.check_unique_inputs(
            subcat_data=subcat_data
        )

        # check subcat permission, edit and parse data
        msg, status_code, _ = cls.auth_by_admin_root(
            get_err="product_subcat_req_ad_priv_to_edit"
        )
        if status_code != 200:
            return None, msg, status_code

        # check if productid exist
        if not productcat:
            return None, {"message": gettext("product_cat_not_found")}, 404

        # check if productid exist
        if not productsubcat:
            return None, {"message": gettext("product_subcat_not_found")}, 404

        if (
            subcatdesc_catid
            and productsubcat
            and subcatdesc_catid.id != productsubcat.id
        ):
            return (
                None,
                {"message": gettext("product_subcat_for_cat_exist")},
                400,  # 400 is for bad request
            )  # 400 is for bad request
        return productsubcat, False, 200
