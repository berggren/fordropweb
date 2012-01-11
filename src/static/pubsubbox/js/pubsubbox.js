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
    connection: null,
    my_jid: null,
    nodes: {},
    roster: {},
    domains: [],
    notifications: 0,
    disco_nodes: {},
    pubsubservice: 'pubsub.example.com',

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

    on_add_to_whitelist: function(nodeID, jid) {
        var iq = $iq({to:XMPP.pubsubservice, type:'set'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub#owner'})
            .c('affiliations', {node:nodeID})
            .c('affiliation', {jid:jid, affiliation:'member' });
        XMPP.connection.sendIQ(iq);
    },

    remove_from_whitelist: function(nodeID, jid) {
        var iq = $iq({to:XMPP.pubsubservice, type:'set'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub#owner'})
            .c('affiliations', {node:nodeID})
            .c('affiliation', {jid:jid, affiliation:'none'});
        XMPP.connection.sendIQ(iq, XMPP.on_remove_from_whitelist(nodeID));
    },

    on_remove_from_whitelist: function(nodeID) {
        setTimeout(function(){
            $(document).trigger('node_update_subscriber_count', {id: nodeID});
        }, 50);
    },

    delete_node: function(nodeID) {
        var iq = $iq({to:XMPP.pubsubservice, type:'set'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub#owner'})
            .c('delete', {node:nodeID});
        $('#' + nodeID).remove();
        XMPP.connection.sendIQ(iq, XMPP.on_whitelist);
    },

    on_roster: function(iq) {
        $("#roster").empty();
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
                var elem = $('<div class="drag box_roster left" jid="' + jid + '" id="' + id + '">' +
                    '<span class="' + id + '-canvas"' + '></span>' +
                    '<span>' + name1 + '<br>' + name2 + '</span></div>');
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
                    XMPP.connection.sendIQ(iq, XMPP.on_pubsub_disco, XMPP.on_error);
                }
            }
        });
        XMPP.connection.send($pres());
    },

    on_pubsub_disco: function(iq) {
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
        $('#discovery').append('<h3>' + XMPP.pubsub_domain(service) + '</h3>');
        for (var n in l) {
            var elem = $('<span id="' + l[n] + '-disco">' + l[n] + '</span><span id="' + l[n] + '-disco-state" class="label success right">subscribe&nbsp;&nbsp;&nbsp;&nbsp;</span><br><br>');
            $(elem).click(function() {
                var nodeID = l[n];
                XMPP.subscribe_to_node(nodeID, XMPP.my_jid, service);
                $(this).text("unsubscribe").removeClass('success');
            });
            $('#discovery').append(elem);
        }
        $('#discovery').append('<hr>');
        var subscriptionIQ =  $iq({to: service, type: 'get'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub'})
            .c('subscriptions');
        XMPP.connection.sendIQ(subscriptionIQ, XMPP.on_get_subscriptions, XMPP.on_error);
    },

    on_get_subscriptions: function(iq) {
        $(iq).find('subscription').each(function(){
            $('#' + $(this).attr('node') + '-disco-state').replaceWith('<span class="label right">unsubscribe</span>')
        })
    },

    subscribe_to_node: function(node, jid, service) {
        var subscribeIQ =  $iq({to: service, type: 'set'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub'})
            .c('subscribe', {"node": node, "jid": jid});
        XMPP.connection.sendIQ(subscribeIQ, XMPP.on_subscribe_to_node, XMPP.on_error);
    },

    on_subscribe_to_node: function(iq) {
    },

    unsubscribe_to_node: function(node, jid, service) {
        var subscribeIQ =  $iq({to: service, type: 'set'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub'})
            .c('unsubscribe', {"node": node, "jid": jid});
        XMPP.connection.sendIQ(subscribeIQ, XMPP.on_unsubscribe_to_node, XMPP.on_error);
    },

    on_unsubscribe_to_node: function(iq) {
    },

    on_roster_changed: function(iq) {
        var rosterIQ = $iq({type: 'get'})
            .c('query', {xmlns: 'jabber:iq:roster'});
        XMPP.connection.sendIQ(rosterIQ, XMPP.on_roster);
    },

    update_notification_count: function(plus_or_minus) {
        if (plus_or_minus === 'plus') {
            XMPP.notifications = XMPP.notifications + 1;
        } else {
            XMPP.notifications = XMPP.notifications - 1;
        }
        if (XMPP.notifications === 0) {
            $('#notification_count').hide();
            $('#subscription_request').hide()
        } else {
            $('#notification_count').replaceWith('<span class="red bold hidden" id="notification_count">' + XMPP.notifications + '</span>');
            $('#notification_count').show();
        }
    },

    on_presence: function(presence)  {
        var type = $(presence).attr('type');
        var from = $(presence).attr('from');
        var from_bare = Strophe.getBareJidFromJid(from);
        if (type === 'subscribe') {
            var id_subscription = XMPP.jid_to_id(from_bare) + '-subscription_request';
            var id_allow = XMPP.jid_to_id(from_bare) + '-subscription_allow';
            var id_deny = XMPP.jid_to_id(from_bare) + '-subscription_deny';
            var elem = '<tr id="' + id_subscription + '"><td>' + from_bare + '</td><td><button class="btn success" id="' + id_allow + '">Yes</button></td><td><span class="btn error" id="' + id_deny + '">No</span></td></tr>';
            $('#subscription_request').show();
            $('#subscription_request_table').append(elem);

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

    on_message: function(message)  {
        var service = $(message).attr('from');
        var node = $(message).find('items').attr('node');
        $(message).find('item').each(function() {
            var payload = $(this).find('event').text();
            $('#activities').append('<span class="alert-message warning"><strong>' + service + '</strong> (' + node + ') ' + payload + '</span><br><br>');
        });
        return true;
    },

    on_vcard: function(iq) {
        var vCard = $(iq).find("vCard");
        var jid = $(iq).attr('from');
        var id = XMPP.jid_to_id(jid);
        var idAvatar = id + '-avatar';
        $('.' + id + '-canvas').append('<canvas id="' + idAvatar + '" width="48" height="48"></canvas><br>');
        var img = vCard.find('BINVAL').text();
        var type = vCard.find('TYPE').text();
        var img_src = 'data:'+type+';base64,'+img;
        var ctx = $('#'+idAvatar).get(0).getContext('2d');
        var image = new Image();
        image.onload = function() {
            ctx.drawImage(image,0,0, 48, 48);
        };
        image.src = img_src;
        $('.drag').draggable({
                                 helper: "clone",
                                 appendTo: "body",
                                 containment: "html",
                                 opacity: "0.85",
                                 revert: false,
                                 revertDuration: 100,
                                 stack: ".drag",
                                 cursor: "move",
                                 scroll: false
                             });
    },

    on_vcard_node_info: function(iq) {
        var vCard = $(iq).find("vCard");
        var jid = $(iq).attr('from');
        var id = XMPP.jid_to_id(jid) + '-node_info';
        var idAvatar = id + '-avatar';
        $('.' + id + '-canvas').append('<canvas id="' + idAvatar + '" width="48" height="48"></canvas><br>');
        var img = vCard.find('BINVAL').text();
        var type = vCard.find('TYPE').text();
        var img_src = 'data:'+type+';base64,'+img;
        var ctx = $('#'+idAvatar).get(0).getContext('2d');
        var image = new Image();
        image.onload = function() {
            ctx.drawImage(image,0,0, 48, 48);
        };
        image.src = img_src;
        $('.drag').draggable({
            helper: "clone",
            appendTo: "body",
            containment: "html",
            opacity: "0.85",
            revert: false,
            revertDuration: 100,
            stack: ".drag",
            cursor: "move",
            scroll: false
        });
    },


    on_my_vcard: function(iq) {
        var vCard = $(iq).find("vCard");
        var base64Image = vCard.find('BINVAL').text();
        var type = vCard.find('TYPE').text();
        var img_src = 'data:'+type+';base64,'+base64Image;
        var ctx = $('#avatar').get(0).getContext('2d');
        var image = new Image();
        image.onload = function() {
            ctx.drawImage(image,0,0,68,68)
        };
        image.src = img_src;
        var jid = $(iq).attr('from');
        var name = vCard.find('FN').text() || jid;
        $("#fullname").text(Strophe.getNodeFromJid(name));
    },

    on_pubsub_item: function(iq) {
        $(iq).find('item').each(function() {
            if ($(this).attr('node') != "/home") {
                XMPP.nodes[$(this).attr('node')] = $(this).attr('name');
            }
        });
        console.log(XMPP.nodes)
        var affiliationIQ = $iq({to: XMPP.pubsubservice, type: 'get'})
            .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub'})
            .c('affiliations');
        XMPP.connection.sendIQ(affiliationIQ, XMPP.on_affiliation, XMPP.on_error);
    },

    on_affiliation: function(iq) {
        $(iq).find('affiliation').each(function() {
            if ($(this).attr('affiliation') === "owner" && $(this).attr('affiliation') != 'outcast') {
                if (XMPP.nodes[$(this).attr('node')]) {
                    var elem = $('<div class="box_node drop left" id="' +
                                    $(this).attr('node') +
                                    '""><strong>' + XMPP.nodes[$(this).attr('node')] +
                                    '</strong><br><br></div>');
                    $("#" + $(this).attr('node')).remove();
                    $(document).trigger('node_subscriber_count', {id: $(elem).attr('id')});
                    $('#pubsub').append(elem);
                    $(elem).click(function() {
                        $('.box_node').removeClass('highlight');
                        $(elem).addClass('highlight');
                        $(document).trigger('node_info', {id: $(elem).attr('id')});
                    });
                    // update fordrop-web database
                    $.ajax({
                        type: 'POST',
                        url: '/api/v1/box/?format=json',
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
        $("#spinner").hide();
        $(iq).find('affiliation').each(function() {
            if ($(this).attr('affiliation') != 'owner' && $(this).attr('affiliation') != 'outcast') {
                var jid = $(this).attr('jid');
                var id = XMPP.jid_to_id(jid) + '-node_info';
                var name = XMPP.roster[jid];
                var splitName = name.split(" ");
                var name1 = splitName[0] || '';
                var name2 = splitName[1] || '';
                var elem = $('<div class="box_roster left" id="' + id + '-node_info">' +
                    '<span class="' + id + '-canvas"' + '></span>' +
                    '<span>' + name1 + '<br>' + name2 + '</span>' +
                    '<div class="vcard_remove hidden" id="remove_from_whitelist"></div>' + '</div>');
                $('#node_info_whitelist').append(elem);
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
                var vCardIQ = $iq({to: jid, type: 'get'})
                    .c('vCard', {xmlns: 'vcard-temp'});
                XMPP.connection.sendIQ(vCardIQ, XMPP.on_vcard_node_info, XMPP.on_error);

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
        $("#" + node).append('<h1 class="count">' + subscribers + '</h1>');
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
        XMPP.connection.sendIQ(pubSubIQ, XMPP.on_pubsub_item, XMPP.on_error);
    },

    on_error: function(iq) {
        if (XMPPConfig.debug === true) {
            console.log('ERROR, take a look ast the followiung error-stanza:');
            console.log(iq);
        }
    }
};

$(document).bind('connect', function(ev, data) {
    var conn = new Strophe.Connection("/http-bind");

//    if (XMPPConfig.debug === true) {
        conn.xmlInput = function (body) {
            console.log(body);
        };
        conn.xmlOutput = function (body) {
            console.log(body);
        };
 //   }
    XMPP.my_jid = data.jid;
    conn.connect(data.jid, data.password, function(status) {
        if (status === Strophe.Status.CONNECTED) {
            $(document).trigger('connected');
            $('#discovery_container').hide();
            $('#notification_container').hide();
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
    $('#label-online').toggle("fast");
    var rosterIQ = $iq({type: 'get'})
        .c('query', {xmlns: 'jabber:iq:roster'});
    var pubSubIQ = $iq({to: XMPP.pubsubservice, type: 'get'})
        .c('query', {xmlns: 'http://jabber.org/protocol/disco#items'});
    var vCardIQ = $iq({type: 'get'})
        .c('query', {xmlns: 'vcard-temp'});
    XMPP.connection.addHandler(XMPP.on_presence, null, "presence");
    XMPP.connection.addHandler(XMPP.on_message, null, "message", "headline");
    XMPP.connection.addHandler(XMPP.on_roster_changed, "jabber:iq:roster", "iq", "set");
    XMPP.connection.sendIQ(rosterIQ, XMPP.on_roster);
    XMPP.connection.sendIQ(pubSubIQ, XMPP.on_pubsub_item, XMPP.on_error);
    XMPP.connection.sendIQ(vCardIQ, XMPP.on_my_vcard, XMPP.on_error);
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
    $("#roster").hide();
    $('#node_info_whitelist').empty().show();
    $("#node_info_buttonlist").empty().show().append('<button id="button_close_node_info" class="btn">&laquo; Back to roster</button>');
    $("#node_info_buttonlist").append('<button id="button_delete_node" class="btn error" style="margin-left:10px;">Delete node</button><br><br>');
    $('#button_delete_node').click(function() {
        XMPP.delete_node(data.id);
        $('#node_info').empty().hide();
        $('#node_info_whitelist').empty().hide();
        $('#node_info_buttonlist').empty().hide();
        $('.box_node').removeClass('highlight');
        $("#roster").fadeIn();
    });
    $('#button_close_node_info').click(function() {
        $('#node_info').empty().hide();
        $('#node_info_whitelist').empty().hide();
        $('#node_info_buttonlist').empty().hide();
        $('.box_node').removeClass('highlight');
        $("#roster").fadeIn();
    });
    var nodeAffiliationIQ = $iq({to: XMPP.pubsubservice, type: 'get'})
        .c('pubsub', {xmlns: 'http://jabber.org/protocol/pubsub#owner'})
        .c('affiliations', {node: data.id});
    XMPP.connection.sendIQ(nodeAffiliationIQ, XMPP.on_node_affiliation)
});

$(document).bind('change_tab', function(event, data) {
    $('#tab_menu').find('li').each(function() {
        $(this).removeClass('active');
    });
    $('#' + data.active_tab).addClass('active');
});

$(document).bind('manage_tab', function(event) {
    $("#roster_container").show();
    $("#nodes_container").show();
    $("#activities_container").hide();
    $("#notification_container").hide();
    $("#discovery_container").hide();
});

$(document).bind('discovery_tab', function(event) {
    $("#roster_container").hide();
    $("#nodes_container").hide();
    $("#activities_container").hide();
    $("#notification_container").hide();
    $("#discovery_container").show();
});

$(document).bind('activities_tab', function(event) {
    $("#roster_container").hide();
    $("#nodes_container").hide();
    $("#notification_container").hide();
    $("#discovery_container").hide();
    $("#activities_container").show();
});

$(document).bind('notification_tab', function(event) {
    $("#roster_container").hide();
    $("#nodes_container").hide();
    $("#activities_container").hide();
    $("#discovery_container").hide();
    $("#notification_container").show();
});

$(document).ready(function() {
    $('#connect-button').click(function() {
        $("#login-form").fadeIn();
    });

    $('#create-node-button').click(function() {
        $("#add-node-modal").modal('hide');
        $(document).trigger('create_node_whitelist', {
                node: $('#node').val()
        });
    });

    $('#add-contact-button').click(function() {
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
        $(document).trigger('connect', {
            jid: $('#jid').val(),
            password: $('#password').val()
        });
        $('#login-screen').hide();
        $('#login-spinner').show();
    })
});
