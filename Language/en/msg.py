# -*- coding: utf-8 -*-
class Common:
    C01 = '[C01]table [{}] not have [{}]! Operator[{}]'
    C02 = '[C02]Function [{}] Completed! Operator[{}]'
    C03 = '[C03]The selected usage time exceeds the current time! Operator[{}]'
    C04 = '[C04]Spot check time exceeds the current time, operator[{}]'


class Verify:
    V01 = '[V01][{}] is not number,Operator[{}]'


class Consumable:
    M01 = '[M01]The consumable [{}] has entered the scrap process, please select other moulds for operation , operator[{}]'
    M02 = '[M02]The consumable [{}] status is not Stock, Can not receive , operator[{}]'
    M03 = '[M03]The consumable [{}] status is not Using, Can not return , operator[{}]'
    M04 = '[M04]The consumable [{}] status is not Using, Can not use , operator[{}]'
    M05 = '[M05]The consumable [{}] location is not [{}], please retype, operator[{}]'
    M06 = '[M06]The consumable [{}] status is not Stock, Can not force scrap , operator[{}]'


class Excel:
    E01 = '[E01]The consumable [{}] already exists in table [{}], operator[{}]'
    E02 = '[E02]The data format is incorrect, operator[{}]'
    E03 = '[E03]The enter time exceeds the current time, operator[{}]'
    E04 = '[E04]The usefullife or ratedlife is incorrect, operator[{}]'
    E05 = '[E05]The location and position cannot exist at the same time, operator[{}]'
    E06 = '[E06]MeasuredValue must be within range StandardValue ± ErrorRange, error digit reference [{}], operator[{}]'
    E07 = '[E07]Only one type of consumable data can be exported to Excel, operator[{}]'
    E08 = '[E08]MeasuredValue and StandardValue can not be empty, operator[{}]'
