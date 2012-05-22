/*
Copyright 2011 NORDUnet A/S. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY NORDUNET A/S ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL NORDUNET A/S OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of NORDUnet A/S.
 */

var XMPP = {
    /*
        Init
     */
    connection: null,
    my_jid: null,
    nodes: {},
    roster: {},
    domains: [],
    notifications: 0,
    disco_nodes: {},

    /*
        Helper functions
     */
    jid_to_id: function(jid) {
        return Strophe.getBareJidFromJid(jid)
        .replace(/@/g, "-")
        .replace(/\./g, "-");
    },

    jid_without_at: function(jid) {
        return Strophe.getBareJidFromJid(jid)
        .replace(/@/g, " ");
    },

    pubsub_domain: function(service) {
        return service.replace(/pubsub\./g, '');
    },

    /*
        XMPP actions
     */

    remove_from_whitelist: function(nodeID, jid) {
        var iq = $iq({to:XMPP.pubsubservice, type:'set'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub#owner'})
            .c('affiliations', {node:nodeID})
            .c('affiliation', {jid:jid, affiliation:'none'});
        XMPP.connection.sendIQ(iq, XMPP.on_remove_from_whitelist(nodeID));
    },

    delete_node: function(nodeID) {
        if (XMPPConfig.debug) {
            console.log("delete node " + nodeID);
        }
        var iq = $iq({to:XMPP.pubsubservice, type:'set'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub#owner'})
            .c('delete', {node:nodeID});
        $('#' + nodeID).fadeOut();
        XMPP.connection.sendIQ(iq, XMPP.on_whitelist);
    },

    subscribe_to_node: function(node, jid, service) {
        var subscribeIQ =  $iq({to: service, type: 'set'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub'})
            .c('subscribe', {"node": node, "jid": jid});
        XMPP.connection.sendIQ(subscribeIQ);
    },

    unsubscribe_from_node: function(node, jid, service) {
        var unsubscribeIQ =  $iq({to: service, type: 'set'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub'})
            .c('unsubscribe', {"node": node, "jid": jid});
        XMPP.connection.sendIQ(unsubscribeIQ);
    },

    update_notification_count: function(plus_or_minus) {
        if (plus_or_minus === 'plus') {
            XMPP.notifications = XMPP.notifications + 1;
        } else {
            XMPP.notifications = XMPP.notifications - 1;
        }
        if (XMPP.notifications === 0) {
            $('#notification_link').hide();
        } else {
            $('#notification_count').text(XMPP.notifications)
            $('#notification_link').show();
        }
    },

    /*
        XMPP event handlers
     */

    on_add_to_whitelist: function(nodeID, jid) {
        var iq = $iq({to:XMPP.pubsubservice, type:'set'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub#owner'})
            .c('affiliations', {node:nodeID})
            .c('affiliation', {jid:jid, affiliation:'member' });
        XMPP.connection.sendIQ(iq);
    },

    on_remove_from_whitelist: function(nodeID) {
        setTimeout(function(){
            $(document).trigger('node_update_subscriber_count', {id: nodeID});
        }, 50);
    },

    on_roster: function(iq) {
        $('.contact').remove();
        $(iq).find('item').each(function() {
            var subscription = $(this).attr('subscription');
            if (subscription === 'both' || subscription === 'from') {
                var jid = $(this).attr('jid');
                var domain = jid.split('@')[1];
                var id = XMPP.jid_to_id(jid);
                var name = $(this).attr('name') || XMPP.jid_without_at(jid);
                XMPP.roster[jid] = name;
                var splitName = name.split(" ");
                var name1 = splitName[0] || '';
                var name2 = splitName[1] || '';
                //var elem = $('<div class="drag contact left" jid="' + jid + '" id="' + id + '">' + '<span style="margin-left:10px;padding-top:5px;"">' + name + '</span><br><span class="quiet" style="margin-left:10px;">' + jid + '</span></div>');
                var elem = $('<div class="drag contact left" jid="' + jid + '" id="' + id + '"><div style="margin-left:10px;">' + name + '</div></div>');
                $('#roster').append(elem);
                var vCardIQ = $iq({to: jid, type: 'get'})
                    .c('vCard', {xmlns: 'vcard-temp'});
                XMPP.connection.sendIQ(vCardIQ, XMPP.on_vcard, XMPP.on_error);
                if ( $.inArray(domain, XMPP.domains) === -1 ) {
                    XMPP.domains.push(domain);
                    var service = 'pubsub.' + domain;
                    var iq =  $iq({to: service, type: 'get'})
                        .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub'})
                        .c('affiliations');
                    XMPP.connection.sendIQ(iq, XMPP.on_discovery, XMPP.on_error);
                }
            }
        });
        XMPP.connection.send($pres());
    },

    on_roster_changed: function(iq) {
        var rosterIQ = $iq({type: 'get'})
            .c('query', {xmlns: 'jabber:iq:roster'});
        XMPP.connection.sendIQ(rosterIQ, XMPP.on_roster);
    },

    on_presence: function(presence) {
        var type = $(presence).attr('type');
        var from = $(presence).attr('from');
        var from_bare = Strophe.getBareJidFromJid(from);
        if (type === 'subscribe') {
            var id_subscription = XMPP.jid_to_id(from_bare) + '-subscription_request';
            var id_allow = XMPP.jid_to_id(from_bare) + '-subscription_allow';
            var id_deny = XMPP.jid_to_id(from_bare) + '-subscription_deny';
            var elem = '<span id="' + id_subscription + '">' + from_bare + '<span class="right"><a href="#" id="' + id_allow + '"><i class="icon-ok-sign"></i> Approve</a> | <a href="#" id="' + id_deny + '"><i class="icon-remove-sign"></i> Reject</a></span></span>';
            $('#notification_link').show();
            $('#notification').append(elem);

            XMPP.update_notification_count('plus');

            $('#' + id_allow).click(function() {
                XMPP.connection.send($pres({
                    to: from_bare,
                    "type": "subscribed"
                }));
                XMPP.connection.send($pres({
                    to: from_bare,
                    "type": "subscribe"
                }));
                $("#" + id_subscription).remove();
                XMPP.update_notification_count('minus')
                var rosterIQ = $iq({type: 'get'})
                    .c('query', {xmlns: 'jabber:iq:roster'});
                XMPP.connection.sendIQ(rosterIQ, XMPP.on_roster);
            });

            $('#' + id_deny).click(function() {
                XMPP.connection.send($pres({
                    to: from_bare,
                    "type": "unsubscribed"
                }));
                $("#" + id_subscription).remove();
                XMPP.update_notification_count('minus')
            });
        }
        return true;
    },

    on_discovery: function(iq) {
        var service = $(iq).attr('from');
        var l = [];
        $(iq).find('affiliation').each(function() {
            if ($(this).attr('affiliation') === 'member') {
                l.push($(this).attr('node'));
            }
        });
        if (l.length < 1) {
            return;
        }
        XMPP.disco_nodes[service] = l;
        $('#discovery').append('<h6>' + XMPP.pubsub_domain(service) + '</h6><br>');
        for (var n in l) {
            var node_name_elem = $('<span class="left"><h4>' + l[n] + '</h4></span>');
            var node_subscribe_elem = $('<a href="#" id="' + l[n] + '-disco-state' + '" class="right" style="margin-top:2px;"><i class="icon-plus-sign"></i> Subscribe</a><br><br>');
            $('#discovery').append(node_name_elem);
            $('#discovery').append(node_subscribe_elem);
            $(node_subscribe_elem).click(function() {
                var nodeID = l[n];
                $(this).replaceWith('<span class="quiet right" style="margin-top:2px;">subscribed</span>')
                XMPP.subscribe_to_node(nodeID, XMPP.my_jid, service);
            });
        }
        var subscriptionIQ =  $iq({to: service, type: 'get'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub'})
            .c('subscriptions');
        XMPP.connection.sendIQ(subscriptionIQ, XMPP.on_get_subscriptions, XMPP.on_error);
    },

    on_get_subscriptions: function(iq) {
        $(iq).find('subscription').each(function(){
            $('#' + $(this).attr('node') + '-disco-state').replaceWith('<span class="quiet right" style="margin-top:2px;">subscribed</span>');
        })
    },

    on_pubsub_event: function(message)  {
        var service = $(message).attr('from');
        var node = $(message).find('items').attr('node');
        $(message).find('item').each(function() {
            var payload = $.parseJSON($(this).find('event').text());
            $('#activities').prepend('<div class="well"><span class="right"><h6>' + service + '</h6></span><span class="left"><b>' + payload.actor + '</b> shared</span><br><br>' + payload.object.hash.sha1 + '</div>');
        });
        var c = $("#activities").children().length;
        if (c > 8) {
            $('#activities div:last').remove().fadeOut();
        }
        return true;
    },

    on_vcard: function(iq) {
        var vCard = $(iq).find("vCard");
        var jid = $(iq).attr('from');
        var id = XMPP.jid_to_id(jid);
        var idAvatar = id + '-canvas';
        var img = vCard.find('BINVAL').text();
        var type = vCard.find('TYPE').text();
        var img_src = 'data:'+type+';base64,'+img;
        if (! img) {
            var elem = $('<span class="left"><img width="40" height="40" src="/site_media/img/placeholder.png"></span><span class="right hide" id="remove_from_whitelist"><i class="icon-trash icon-white"></i></span>');
        } else {
            var elem = $('<span class="left"><img width="40" height="40" src="' + img_src + '"></span><span class="right hide" id="remove_from_whitelist"><i class="icon-trash icon-white"></i></span>');
            sessionStorage.setItem(id, img_src);
        }
        $('#' + id).prepend(elem);
        $('.drag').draggable({
                                 helper: "clone",
                                 appendTo: "body",
                                 containment: "nodes",
                                 opacity: "0.85",
                                 revert: false,
                                 revertDuration: 100,
                                 stack: ".drag",
                                 cursor: "move",
                                 scroll: false
                             });
    },

    on_nodes: function(iq) {
        $(iq).find('item').each(function() {
            if ($(this).attr('node') != "/home") {
                XMPP.nodes[$(this).attr('node')] = $(this).attr('name');
            }
        });
        var affiliationIQ = $iq({to: XMPP.pubsubservice, type: 'get'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub'})
            .c('affiliations');
        XMPP.connection.sendIQ(affiliationIQ, XMPP.on_affiliation, XMPP.on_error);
    },

    on_affiliation: function(iq) {
        $('#add_node').show();
        $(iq).find('affiliation').each(function() {
            if ($(this).attr('affiliation') === "owner" && $(this).attr('affiliation') != 'outcast') {
                if (XMPP.nodes[$(this).attr('node')]) {
                    var elem = $('<div class="node drop left" id="' +
                                    $(this).attr('node') +
                                    '""><br><strong>' + XMPP.nodes[$(this).attr('node')] +
                                    '</strong><br></div>');
                    $("#" + $(this).attr('node')).remove();
                    $(document).trigger('node_subscriber_count', {id: $(elem).attr('id')});
                    $('#nodes').append(elem);
                    $(elem).click(function() {
                        $('.node').css({opacity:0.2});
                        $('.add-node').css({opacity:0.2});
                        $(elem).css({opacity:1.0});
                        $(document).trigger('node_info', {id: $(elem).attr('id')});
                    });
                    $.ajax({
                        type: 'POST',
                        url: '/federation/node/add/',
                        data: '{"node":"' + $(this).attr("node") + '", "name":"' + XMPP.nodes[$(this).attr("node")] + '"}',
                        dataType: "application/json",
                        processData:  false,
                        contentType: "application/json"
                    });
                    $(".drop").droppable({
                        drop: function(event, ui) {
                            var jid = ui.draggable.attr('jid');
                            var nodeID = $(this).attr('id');
                            XMPP.on_add_to_whitelist(nodeID, jid);
                            $(document).trigger('node_update_subscriber_count', {id: nodeID});
                        }
                    });
                }
            }
        });
    },

    on_node_affiliation: function(iq) {
        $(iq).find('affiliation').each(function() {
            if ($(this).attr('affiliation') != 'owner' && $(this).attr('affiliation') != 'outcast') {
                var jid = $(this).attr('jid');
                var id = XMPP.jid_to_id(jid);
                var name = XMPP.roster[jid];
                var avatar = sessionStorage.getItem(id);
                if ( ! avatar ) {
                    var elem = $('<div jid="' + jid + '" id="' + id + '" class="contact left"><span class="avatar left"><img width="40" height="40" src="/site_media/img/placeholder.png"></span><span style="margin-left:10px;padding-top:5px;">' + name + '</span><span class="right hide" id="remove_from_whitelist"><i class="icon-trash"></i></span><br><span class="quiet" style="margin-left:10px;">' + jid + '</span></div>');
                } else {
                    var elem = $('<div jid="' + jid + '" id="' + id + '" class="contact left"><span class="avatar left"><img width="40" height="40" src="' + avatar + '"></span><span style="margin-left:10px;padding-top:5px;">' + name + '</span><span class="right hide" id="remove_from_whitelist"><i class="icon-trash"></i></span><br><span class="quiet" style="margin-left:10px;">' + jid + '</span></div>');
                }
                $('#roster2').append(elem);
                $(elem).mouseenter(function() {
                    $(elem).find('#remove_from_whitelist').show()
                });
                $(elem).mouseleave(function() {
                    $(elem).find('#remove_from_whitelist').hide()
                });
                $(elem).find('#remove_from_whitelist').click(function() {
                    var nodeID = $(iq).find('affiliations').attr('node');
                    XMPP.remove_from_whitelist(nodeID, jid);
                    $(this).parent().empty().hide();
                });
            }
        });
    },

    on_node_subscriber_count: function(iq) {
        var subscribers = 0;
        var node = $(iq).find('affiliations').attr('node');
        $(iq).find('affiliation').each(function() {
            if ($(this).attr('affiliation') != 'owner'&& $(this).attr('affiliation') != 'outcast') {
                subscribers =  subscribers + 1;
            }
        });
        $("#" + node).append('<br><h1 class="count">' + subscribers + '</h1>');
    },

    on_node_update_subscriber_count: function(iq) {
        var subscribers = 0;
        var node = $(iq).find('affiliations').attr('node');
        $(iq).find('affiliation').each(function() {
            if ($(this).attr('affiliation') != 'owner' && $(this).attr('affiliation') != 'outcast') {
                subscribers =  subscribers + 1;
            }
        });
        $("#" + node).find('h1').replaceWith('<h1 class="count">' + subscribers + '</h1>');
    },

    on_create_node_whitelist: function(iq) {
        var pubSubIQ = $iq({to: XMPP.pubsubservice, type: 'get'})
            .c('query', {xmlns: 'http://jabber.org/protocol/disco#items'});
        XMPP.connection.sendIQ(pubSubIQ, XMPP.on_nodes, XMPP.on_error);
    },

    on_error: function(iq) {
        if (XMPPConfig.debug) {
            console.log('ERROR, take a look at the following error-stanza:');
            console.log(iq);
        }
    }
};

$(document).bind('connect', function(ev, data) {
    var conn = new Strophe.Connection("/http-bind");
    if (XMPPConfig.debug) {
        conn.xmlInput = function (body) {
            console.log(body);
        };
        conn.xmlOutput = function (body) {
            console.log(body);
        };
    }
    XMPP.my_jid = data.jid;
    XMPP.pubsubservice = data.pubsubservice;
    conn.connect(data.jid, data.password, function(status) {
        if    (status === Strophe.Status.CONNECTED) {
            $(document).trigger('connected');
        } else if (status === Strophe.Status.CONNECTING) {
            $('#conn-fail').hide();
        } else if (status === Strophe.Status.AUTHFAIL) {
            $('#login-screen').show();
            $('#login-spinner').hide();
            $('#conn-fail').show();
        } else if (status === Strophe.Status.CONNFAIL) {
            $('#login-screen').show();
            $('#login-spinner').hide();
            $('#conn-fail').show();
        } else if (status === Strophe.Status.DISCONNECTED) {
            $(document).trigger('disconnected');
        }
    });
    XMPP.connection = conn;
});

$(document).bind('connected', function () {
    $('#login-spinner').hide();
    $('#main-screen').toggle("fast");
    var rosterIQ = $iq({type: 'get'})
        .c('query', {xmlns: 'jabber:iq:roster'});
    var pubSubIQ = $iq({to: XMPP.pubsubservice, type: 'get'})
        .c('query', {xmlns: 'http://jabber.org/protocol/disco#items'});
    XMPP.connection.addHandler(XMPP.on_presence, null, "presence");
    XMPP.connection.addHandler(XMPP.on_pubsub_event, null, "message", "headline");
    XMPP.connection.addHandler(XMPP.on_roster_changed, "jabber:iq:roster", "iq", "set");
    XMPP.connection.sendIQ(rosterIQ, XMPP.on_roster);
    XMPP.connection.sendIQ(pubSubIQ, XMPP.on_nodes, XMPP.on_error);

});

$(document).bind('disconnected', function () {
    $('#label-online').removeClass('success').addClass('important').text("Offline");
    XMPP.connection = null;
});

$(document).bind('create_node_whitelist', function(event, data) {
    var iq = $iq({to:XMPP.pubsubservice, type:'set'})
        .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub'})
        .c('create')
        .up()
        .c('configure')
        .c('x', {xmlns: 'jabber:x:data', type: "submit"})
        .c('field', {"var": "FORM_TYPE", type: "hidden"})
        .c('value').t('http://jabber.org/protocol/pubsub#node_config')
        .up().up()
        .c('field', {"var": 'pubsub#access_model'})
        .c('value').t("whitelist")
        .up().up()
        .c('field', {"var": 'pubsub#title'})
        .c('value').t(data.node);
    XMPP.connection.sendIQ(iq, XMPP.on_create_node_whitelist);
});

$(document).bind('add_contact', function(event, data) {
    XMPP.connection.send($pres({
        to: data.jid,
        "type": "subscribe"
    }))
});

$(document).bind('node_subscriber_count', function(event, data) {
    var nodeCountIQ = $iq({to: XMPP.pubsubservice, type: 'get'})
        .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub#owner'})
        .c('affiliations', {node: data.id});
    XMPP.connection.sendIQ(nodeCountIQ, XMPP.on_node_subscriber_count, XMPP.on_error)
});

$(document).bind('node_update_subscriber_count', function(event, data) {
    var nodeCountIQ = $iq({to: XMPP.pubsubservice, type: 'get'})
        .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub#owner'})
        .c('affiliations', {node: data.id});
    XMPP.connection.sendIQ(nodeCountIQ, XMPP.on_node_update_subscriber_count, XMPP.on_error)
});

$(document).bind('node_info', function(event, data) {
    $('#roster').hide();
    $('#roster2').empty().show();
    $('#manage_link').show();
    //$('#roster2').append('<span style="font-size:25px; margin-right:20px; margin-top:3px;font-weight:300; "Helvetica Neue,Helvetica,Arial,sans-serif">' + XMPP.nodes[data.id] + '</span><a href="#" id="delete_node"><i class="icon-trash"></i></a>&nbsp;<a href="#" id="close_node"><i class="icon-remove-circle"></i></a><br><br>');
    var nodeAffiliationIQ = $iq({to: XMPP.pubsubservice, type: 'get'})
        .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub#owner'})
        .c('affiliations', {node: data.id});
    $("#delete_node").click(function() {
        $('.node').css({opacity:1.0});
        $('.add-node').css({opacity:1.0});
        $("#roster2").hide();
        $("#roster").fadeIn('fast');
        XMPP.delete_node(data.id);
    });
    $('#close_node').click(function() {
        $('.node').css({opacity:1.0});
        $('.add-node').css({opacity:1.0});
        $('#roster2').fadeOut('fast');
        $("#roster").fadeIn('fast');
    });
    XMPP.connection.sendIQ(nodeAffiliationIQ, XMPP.on_node_affiliation)
});

$(document).bind('change_tab', function(event, data) {
    $('#tab_menu').find('li').each(function() {
        $(this).removeClass('active');
    });
    $('#' + data.active_tab).addClass('active');
});

$(document).bind('manage_tab', function(event) {
    $('.node').css({opacity:1.0});
    $('.add-node').css({opacity:1.0});
    $('#manage_link').hide();
    $('#roster2').fadeOut('fast');
    $("#roster").fadeIn('fast');
    $("#nodes").show();
    $("#discovery").hide();
    $("#activities").hide();
    $("#notification").hide();
    $("#add-node").show();
});

$(document).bind('discovery_tab', function(event) {
    $('.node').css({opacity:1.0});
    $('#roster2').fadeOut('fast');
    $("#roster").fadeIn('fast');
    $("#nodes").hide();
    $("#discovery").fadeIn('fast');
    $("#activities").hide();
    $("#notification").hide();
    $("#add-node").hide();

});

$(document).bind('activities_tab', function(event) {
    $('.node').css({opacity:1.0});
    $('#roster2').fadeOut('fast');
    $("#roster").fadeIn('fast');
    $("#nodes").hide();
    $("#discovery").hide();
    $("#activities").fadeIn('fast');
    $("#notification").hide();
    $("#add-node").hide();
});

$(document).bind('notification_tab', function(event) {
    $('.node').css({opacity:1.0});
    $('#roster2').fadeOut('fast');
    $("#roster").fadeIn('fast');
    $("#nodes").hide();
    $("#discovery").hide();
    $("#activities").hide();
    $("#notification").fadeIn('fast');
    $("#add-node").hide();
});

$(document).ready(function() {
    $('#connect-button').click(function() {
        $("#login-form").fadeIn();
    });

    $('#add-node').click(function() {
        $("#add-node-modal").modal('show');
    });

    $('#add-contact').click(function() {
        $("#add-contact-modal").modal('show');
    });

    $('#create-node-button').click(function() {
        $("#add-node-modal").modal('hide');
        $(document).trigger('create_node_whitelist', {
                node: $('#node').val()
        });
    });

    $('#create-contact-button').click(function() {
        $("#add-contact-modal").modal('hide');
    });

    $('#create-contact-button').click(function() {
        $("#add-contact-modal").modal('hide');
        $(document).trigger('add_contact', {
            jid: $('#contact').val()
        });
    });

    $('#activities_link').click(function() {
        $(document).trigger('change_tab', {
                active_tab: 'activities_tab'});
        $(document).trigger('activities_tab');
    });

    $('#manage_link').click(function() {
        $(document).trigger('change_tab', {
                active_tab: 'manage_tab'});
        $(document).trigger('manage_tab');
    });

    $('#discovery_link').click(function() {
        $(document).trigger('change_tab', {
            active_tab: 'discovery_tab'});
        $(document).trigger('discovery_tab');
    });

    $('#notification_link').click(function() {
        $(document).trigger('change_tab', {
            active_tab: 'notification_tab'});
        $(document).trigger('notification_tab');
    });

    $('#login-button').click(function() {
        $('#login-screen').hide();
        $('#login-spinner').fadeIn();
            $(document).trigger('connect', {
                jid: XMPPConfig.jid,
                password: $('#password').val(),
                pubsubservice: XMPPConfig.pubsubservice
            });
    })
});
