# -*- coding: utf-8 -*-
from openerp import models,fields,api
from openerp.tools.translate import _
import datetime
from openerp.exceptions import Warning
import codecs
import unicodedata


def s(txt):
    if type(txt)!=unicode:
        txt = unicode(txt,'utf-8')
    txt = unicodedata.normalize('NFD', txt).encode('ascii', 'ignore')
    return txt


class is_export_compta(models.Model):
    _name='is.export.compta'
    _order='name desc'

    name               = fields.Char("N°Folio"      , readonly=True)
    #journal_id         = fields.Many2one('account.journal', 'Journal')
    journal = fields.Selection([
        ('CAI', 'Caisse'),
        ('HA' , 'Achats'),
    ], 'Journal', default='CAI')
    date_debut         = fields.Date("Date de début", required=True)
    date_fin           = fields.Date("Date de fin"  , required=True)
    ligne_ids          = fields.One2many('is.export.compta.ligne', 'export_compta_id', u'Lignes')
    _defaults = {
    }


    @api.model
    def create(self, vals):
        data_obj = self.env['ir.model.data']
        sequence_ids = data_obj.search([('name','=','is_export_compta_seq')])
        if sequence_ids:
            sequence_id = data_obj.browse(sequence_ids[0].id).res_id
            vals['name'] = self.env['ir.sequence'].get_id(sequence_id, 'id')
        res = super(is_export_compta, self).create(vals)
        return res





    @api.multi
    def action_export_compta2(self):
        cr=self._cr
        for obj in self:
            obj.ligne_ids.unlink()

            if obj.journal=='CAI':
                sql="""
                    SELECT  
                        aml.date,
                        aa.code, 
                        aa.name,
                        '',
                        '',
                        '',
                        sum(aml.credit)-sum(aml.debit)
                    FROM account_move_line aml left outer join account_invoice ai        on aml.move_id=ai.move_id
                                               inner join account_account aa             on aml.account_id=aa.id
                                               left outer join res_partner rp            on aml.partner_id=rp.id
                                               inner join account_journal aj             on aml.journal_id=aj.id
                    WHERE 
                        aml.date>='"""+str(obj.date_debut)+"""' and 
                        aml.date<='"""+str(obj.date_fin)+"""' and 
                        ((aa.code>'411100' and aa.code not like '512%') or aa.code='411000') and 
                        aj.type in ('sale','bank','general','cash')
                    GROUP BY aml.date, aa.code, aa.name
                    ORDER BY aml.date, aa.code, aa.name
                """


            if obj.journal=='HA':
                sql="""
                    SELECT  
                        aml.date,
                        aa.code, 
                        aa.name,
                        aj.code,
                        ai.number,
                        rp.name,
                        sum(aml.credit)-sum(aml.debit)
                    FROM account_move_line aml left outer join account_invoice ai        on aml.move_id=ai.move_id
                                               inner join account_account aa             on aml.account_id=aa.id
                                               left outer join res_partner rp            on aml.partner_id=rp.id
                                               inner join account_journal aj             on aml.journal_id=aj.id
                    WHERE 
                        aml.date>='"""+str(obj.date_debut)+"""' and 
                        aml.date<='"""+str(obj.date_fin)+"""' and 
                        aj.code='FACTU'
                    GROUP BY ai.number,aml.date, aa.code, aa.name,aj.code,rp.name
                    ORDER BY ai.number,aml.date, aa.code, aa.name,aj.code,rp.name
                """
            cr.execute(sql)
            for row in cr.fetchall():
                print row
                montant=row[6]
                debit=0
                credit=0
                if montant<0:
                    debit=-montant
                else:
                    credit=montant


                date_facture=row[0]

                date=date_facture
                date=datetime.datetime.strptime(date, '%Y-%m-%d')
                date=date.strftime('%d/%m/%Y')

                libelle_piece='Caisse du '+date
                if obj.journal=='HA':
                    libelle_piece=row[5]

                if montant:
                    vals={
                        'export_compta_id'  : obj.id,
                        'date_facture'      : date_facture,
                        'compte'            : row[1],
                        'libelle'           : s(row[2]),
                        'piece'             : row[4],
                        'libelle_piece'     : libelle_piece,
                        'journal'           : obj.journal,
                        'debit'             : debit,
                        'credit'            : credit,
                        'devise'            : u'EUR',
                    }


                    self.env['is.export.compta.ligne'].create(vals)
            self.generer_fichier2()


    def generer_fichier2(self):
        for obj in self:
            model='is.export.compta'
            attachments = self.env['ir.attachment'].search([('res_model','=',model),('res_id','=',obj.id)])
            attachments.unlink()
            name='export-compta.txt'
            dest     = '/tmp/'+name
            f = codecs.open(dest,'wb',encoding='utf-8')

            f.write('##Transfert\r\n')
            f.write('##Section\tDos\r\n')
            f.write('EUR\r\n')
            f.write('##Section\tMvt\r\n')
            for row in obj.ligne_ids:
                compte=str(row.compte or '')
                debit=row.debit
                credit=row.debit
                if row.credit>0.0:
                    montant=row.credit  
                    sens='C'
                else:
                    montant=row.debit  
                    sens='D'
                montant='%0.2f' % montant
                date=row.date_facture
                date=datetime.datetime.strptime(date, '%Y-%m-%d')
                date=date.strftime('%d/%m/%Y')


                #libelle=row.libelle or u'??'
                #libelle2='Caisse du '+date
                #if obj.journal=='HA':
                #    libelle2='x'

                f.write('"'+obj.name+'"\t')
                f.write('"'+obj.journal+'"\t')
                f.write('"'+date+'"\t')
                f.write('"'+compte+'"\t')
                f.write('"'+row.libelle+'"\t')
                f.write('"'+montant+'"\t')
                f.write(sens+'\t')
                f.write('B\t')
                f.write('"'+row.libelle_piece+'"\t')
                f.write('"'+row.piece+'"\t') #N°de pièce vide
                f.write('\r\n')
            f.write('##Section\tJnl\r\n')
            f.write('"CAI"\t"Caisse"\t"T"\r\n')
            f.close()
            r = open(dest,'rb').read().encode('base64')
            vals = {
                'name':        name,
                'datas_fname': name,
                'type':        'binary',
                'res_model':   model,
                'res_id':      obj.id,
                'datas':       r,
            }
            id = self.env['ir.attachment'].create(vals)


















    @api.multi
    def action_export_compta(self):
        cr=self._cr
        for obj in self:
            obj.ligne_ids.unlink()
            sql="""
                SELECT  
                    aml.date,
                    aa.code, 
                    aa.name,
                    sum(aml.credit)-sum(aml.debit)
                FROM account_move_line aml left outer join account_invoice ai        on aml.move_id=ai.move_id
                                           inner join account_account aa             on aml.account_id=aa.id
                                           left outer join res_partner rp            on aml.partner_id=rp.id
                                           inner join account_journal aj             on aml.journal_id=aj.id
                WHERE 
                    aml.date>='"""+str(obj.date_debut)+"""' and 
                    aml.date<='"""+str(obj.date_fin)+"""' and
                    ((aa.code>'411100' and aa.code not like '512%') or aa.code='411000') and 
                    aj.type in ('sale','bank','general','cash')
                GROUP BY aml.date, aa.code, aa.name
                ORDER BY aml.date, aa.code, aa.name
            """
            cr.execute(sql)
            for row in cr.fetchall():
                montant=row[3]
                debit=0
                credit=0
                if montant<0:
                    debit=-montant
                else:
                    credit=montant
                if montant:
                    vals={
                        'export_compta_id'  : obj.id,
                        'date_facture'      : row[0],
                        'compte'            : row[1],
                        'libelle'           : s(row[2]),
                        'journal'           : 'CAI',
                        'debit'             : debit,
                        'credit'            : credit,
                        'devise'            : u'EUR',
                    }
                    self.env['is.export.compta.ligne'].create(vals)
            self.generer_fichier()


    def generer_fichier(self):
        for obj in self:
            model='is.export.compta'
            attachments = self.env['ir.attachment'].search([('res_model','=',model),('res_id','=',obj.id)])
            attachments.unlink()
            name='export-compta.txt'
            dest     = '/tmp/'+name
            f = codecs.open(dest,'wb',encoding='utf-8')

            f.write('##Transfert\r\n')
            f.write('##Section\tDos\r\n')
            f.write('EUR\r\n')
            f.write('##Section\tMvt\r\n')
            for row in obj.ligne_ids:
                compte=str(row.compte or '')
                debit=row.debit
                credit=row.debit
                if row.credit>0.0:
                    montant=row.credit  
                    sens='C'
                else:
                    montant=row.debit  
                    sens='D'
                montant='%0.2f' % montant
                date=row.date_facture
                date=datetime.datetime.strptime(date, '%Y-%m-%d')
                date=date.strftime('%d/%m/%Y')
                libelle=row.libelle or u'??'
                f.write('"'+obj.name+'"\t')
                f.write('"CAI"\t')
                f.write('"'+date+'"\t')
                f.write('"'+compte+'"\t')
                f.write('"'+libelle+'"\t')
                f.write('"'+montant+'"\t')
                f.write(sens+'\t')
                f.write('B\t')
                f.write('"Caisse du '+date+'"\t')
                f.write('""\t') #N°de pièce vide
                f.write('\r\n')
            f.write('##Section\tJnl\r\n')
            f.write('"CAI"\t"Caisse"\t"T"\r\n')
            f.close()
            r = open(dest,'rb').read().encode('base64')
            vals = {
                'name':        name,
                'datas_fname': name,
                'type':        'binary',
                'res_model':   model,
                'res_id':      obj.id,
                'datas':       r,
            }
            id = self.env['ir.attachment'].create(vals)


class is_export_compta_ligne(models.Model):
    _name = 'is.export.compta.ligne'
    _description = u"Lignes d'export en compta"
    _order='date_facture'

    export_compta_id = fields.Many2one('is.export.compta', 'Export Compta', required=True, ondelete='cascade')
    date_facture     = fields.Date("Date")
    journal          = fields.Char("Journal")
    compte           = fields.Char("N°Compte")
    libelle          = fields.Char("Libellé Compte")
    piece            = fields.Char("Pièce")
    libelle_piece    = fields.Char("Libellé Piece")
    debit            = fields.Float("Débit")
    credit           = fields.Float("Crédit")
    devise           = fields.Char("Devise")
    commentaire      = fields.Char("Commentaire")

    _defaults = {
        'journal': 'VTE',
        'devise' : 'E',
    }







