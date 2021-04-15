from openerp import _, http


class GEDSimplifiedController(http.Controller):

    @http.route('/partner/directory_path', type='json', auth='public')
    def get_partner_directory_path_for_os(self, **kwargs):
        os_source = http.request.httprequest.environ["HTTP_USER_AGENT"]
        partner = http.request.env["res.partner"].search([["id", "=", kwargs["partner_id"]]], None, 1)
        if not partner:
            raise Exception(_("No partner with the id " + kwargs["partner_id"] + " was found."))
        return {
            "partner_docs_path": partner.directory_id_mf_absolute_path if "Linux" in os_source else partner.directory_id_mf_absolute_path_windows,
            "os": os_source
        }
